# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import unittest.mock

from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_run_log_execution_result_enabled():
    with unittest.mock.patch.dict(
        os.environ,
        {
            "VDK_LOG_EXECUTION_RESULT": "True",
        },
    ):
        runner = CliEntryBasedTestRunner()

        result: Result = runner.invoke(["run", util.job_path("simple-job")])

        cli_assert_equal(0, result)
        assert "Data Job execution summary" in result.output
        assert "steps_list" in result.output


def test_run_log_execution_result_enabled_on_fail():
    with unittest.mock.patch.dict(
        os.environ,
        {
            "VDK_LOG_EXECUTION_RESULT": "True",
        },
    ):
        runner = CliEntryBasedTestRunner()

        result: Result = runner.invoke(["run", util.job_path("fail-job")])

        cli_assert_equal(1, result)
        assert "Data Job execution summary" in result.output
        assert "steps_list" in result.output


def test_run_log_execution_result_disabled():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("simple-job")])

    cli_assert_equal(0, result)
    assert "Data Job execution summary" not in result.output
    assert "steps_list" not in result.output
    assert "Job execution result: SUCCESS" in result.output


def test_run_log_execution_result_disabled_on_fail():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job")])

    cli_assert_equal(1, result)
    assert "Data Job execution summary" not in result.output
    assert "steps_list" not in result.output
    assert "Job execution result: ERROR" in result.output
