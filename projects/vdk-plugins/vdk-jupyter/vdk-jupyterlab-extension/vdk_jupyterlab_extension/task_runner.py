# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import threading


class TaskRunner:
    def __init__(self):
        self.__task_status = {
            "task_type": None,
            "status": "idle",
            "message": None,
            "error": None,
        }
        self.lock = threading.Lock()

    def start_task(self, task_type, task_handler):
        with self.lock:
            if self.__task_status["status"] != "idle":
                return False

            self.__task_status = {
                "task_type": task_type,
                "status": "running",
                "message": f"Task {task_type} started",
                "error": None,
            }

        thread = threading.Thread(target=self._run_task, args=(task_handler,))
        thread.start()
        return True

    def get_status(self):
        with self.lock:
            return self.__task_status.copy()

    def _run_task(self, task_handler):
        try:
            result = task_handler()
            with self.lock:
                self.__task_status = {
                    "task_type": self.__task_status["task_type"],
                    "status": "completed",
                    "message": result,
                    "error": None,
                }
        except Exception as e:
            with self.lock:
                self.__task_status = {
                    "task_type": self.__task_status["task_type"],
                    "status": "error",
                    "message": None,
                    "error": str(e),
                }
