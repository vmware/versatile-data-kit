# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import threading
import time
from unittest.mock import Mock

import pytest
from vdk_jupyterlab_extension.task_runner import TaskRunner


@pytest.fixture
def task_runner():
    return TaskRunner()


def test_start_task(task_runner):
    def task():
        time.sleep(0.2)
        return "Task completed successfully"

    task_handler = Mock(side_effect=task)

    task_type = "TEST"
    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    status = task_runner.get_status()
    assert status["task_id"] == task_id
    assert status["status"] == "running"

    time.sleep(0.3)

    status = task_runner.get_status()
    assert status["status"] == "completed"
    assert status["message"] == "Task completed successfully"
    assert status["error"] is None


def test_task_completion(task_runner):
    completed_event = threading.Event()
    task_handler = Mock(
        side_effect=lambda: (completed_event.set(), "Task completed successfully")[1]
    )
    task_type = "TEST"
    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    completed_event.wait(1)
    time.sleep(0.1)

    status = task_runner.get_status()
    assert status["status"] == "completed"
    assert status["message"] == "Task completed successfully"


def test_task_error(task_runner):
    task_handler = Mock(side_effect=Exception("An error occurred"))
    task_type = "TEST"
    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    time.sleep(0.1)
    status = task_runner.get_status()
    assert status["status"] == "failed"
    assert "An error occurred" in status["error"]


def test_task_status_after_completion(task_runner):
    completed_event = threading.Event()
    task_handler = Mock(side_effect=lambda: completed_event.set())
    task_type = "TEST"
    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    completed_event.wait(1)
    time.sleep(0.1)

    status = task_runner.get_status()
    assert (
        status["status"] == "completed"
    ), f"Task {task_type} did not complete before attempting to restart"
    assert (
        task_runner.start_task(task_type, task_handler) is not None
    ), "Unable to start a new task after completion"


def test_task_status_fail_then_success(task_runner):
    task_handler = Mock(
        side_effect=[Exception("An error occurred"), "Task completed successfully"]
    )
    task_type = "TEST"
    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    time.sleep(0.1)
    status = task_runner.get_status()
    assert status["status"] == "failed"
    assert "An error occurred" in status["error"]

    task_id = task_runner.start_task(task_type, task_handler)
    assert task_id is not None

    time.sleep(0.1)
    status = task_runner.get_status()
    assert status["status"] == "completed"
    assert status["message"] == "Task completed successfully"
