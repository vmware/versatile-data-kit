# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import threading
import uuid


class TaskRunner:
    """
    Manages the execution of a single asynchronous task at a time.

    This class provides functionality to start, monitor, and manage the status of an asynchronous task.
    It ensures that only one task runs at any given time and provides the ability to poll for the current
    status of the task.

    Attributes:
        __task_status (dict): A dictionary storing the current status of the task.
        lock (threading.Lock): A lock to synchronize access to the task status.

    Methods:
        start_task(task_type, task_handler): Starts a new task if no other task is running.
        get_status(): Returns the current status of the task.
        _run_task(task_handler): Private method to handle task execution.
    """

    def __init__(self):
        self.__task_status = {
            "task_id": None,
            "status": "idle",
            "message": None,
            "error": None,
        }
        self.lock = threading.Lock()

    def start_task(self, task_type, task_handler):
        """
        Starts a new task of the specified type if no other task is currently running.

        :param task_type: A string representing the type of the task.
        :param task_handler: The function to be executed for this task.
        :return: The unique task ID if the task was successfully created, None otherwise (if another task is running).
        """
        task_id = f"{task_type}-{str(uuid.uuid4())}"
        with self.lock:
            if self.__task_status["status"] not in ["idle", "completed", "failed"]:
                return None

            self.__task_status = {
                "task_id": task_id,
                "status": "running",
                "message": f"Task {task_id} started",
                "error": None,
            }

            thread = threading.Thread(target=self._run_task, args=(task_handler,))
            thread.start()
            return task_id

    def get_status(self):
        """
        Retrieves the current status of the task being managed by the TaskRunner.
        :return: A dictionary containing the current status of the task.
        """
        with self.lock:
            return self.__task_status.copy()

    def _run_task(self, task_handler):
        """
        Executes the given task handler function in a separate thread and updates the task status.
        :param task_handler: The function to be executed for this task.
        :return:
        """
        try:
            result = task_handler()
            with self.lock:
                self.__task_status = {
                    "task_id": self.__task_status["task_id"],
                    "status": "completed",
                    "message": result,
                    "error": None,
                }
        except Exception as e:
            with self.lock:
                self.__task_status = {
                    "task_id": self.__task_status["task_id"],
                    "status": "failed",
                    "message": None,
                    "error": str(e),
                }
