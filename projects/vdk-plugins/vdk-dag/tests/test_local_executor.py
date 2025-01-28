# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import time
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.dag import dag_plugin
from vdk.plugin.dag.local_executor import LocalDataJobExecutor
from vdk.plugin.dag.remote_data_job import JobStatus
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.fixture(scope="session", autouse=True)
def reduce_retries_in_test_http_requests():
    """
    In order to speed up failures, not wait all re-tries with backoffs (which can be minutes)
    we are reconfiguring the vdk-control-cli to have single retry (1st retry is attempted immediately so no slow down)
    """
    with mock.patch.dict(
        os.environ,
        {
            "DAGS_LOCAL_RUN_JOB_PATH": jobs_path_from_caller_directory(""),
            "DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS": "0",
            "DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS": "0",
        },
    ) as _fixture:
        yield _fixture


def wait_for_result(func, expected_result, timeout_seconds):
    """Call func until it returns 'SUCCEEDED' or timeout expires."""
    end_time = time.time() + timeout_seconds
    result = ""
    while time.time() < end_time:
        result = func()
        if result == expected_result:
            return True
        time.sleep(0.2)
    raise TimeoutError(
        f"Function {func} did not return '{expected_result}' within timeout period. Last result was {result}"
    )


def test_local_run(tmp_path):
    executor = LocalDataJobExecutor()

    test_file = tmp_path / "file"
    eid = executor.start_job("write-file-job", "", "", dict(path=str(test_file)))

    assert executor.status_job("write-file-job", "", eid) == JobStatus.RUNNING.value

    wait_for_result(
        lambda: executor.status_job("write-file-job", "", eid),
        JobStatus.SUCCEEDED.value,
        10,
    )

    assert test_file.read_text() == "data"


def test_local_run_failure(tmp_path):
    executor = LocalDataJobExecutor()

    eid = executor.start_job("fail-job", "", "")

    assert executor.status_job("fail-job", "", eid) == JobStatus.RUNNING.value

    wait_for_result(
        lambda: executor.status_job("fail-job", "", eid), JobStatus.USER_ERROR.value, 10
    )


def test_dag_local():
    with mock.patch.dict(
        os.environ,
        {
            "DAGS_JOB_EXECUTOR_TYPE": "local",
        },
    ):
        runner = CliEntryBasedTestRunner(dag_plugin)

        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("local-dag"),
            ]
        )

        cli_assert_equal(0, result)
