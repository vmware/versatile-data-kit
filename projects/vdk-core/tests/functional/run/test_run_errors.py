# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from typing import Dict
from unittest import mock

import pytest
from click.testing import Result
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IPropertiesServiceClient
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import TestPropertiesPlugin


@pytest.fixture(autouse=True)
def tmp_termination_msg_file(tmpdir) -> pathlib.Path:
    out_file = str(tmpdir.join("termination-log"))
    with mock.patch.dict(
        os.environ,
        {
            "VDK_TERMINATION_MESSAGE_WRITER_ENABLED": "true",
            "VDK_TERMINATION_MESSAGE_WRITER_OUTPUT_FILE": out_file,
        },
    ):
        yield pathlib.Path(out_file)


def test_initialize_step_user_error(tmp_termination_msg_file):
    errors.clear_intermediate_errors()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("syntax-error-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_user_error(tmp_termination_msg_file):
    errors.clear_intermediate_errors()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_user_error_fail_job_library(tmp_termination_msg_file):
    errors.clear_intermediate_errors()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job-indirect-library")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_user_error_fail_job_ingest_iterator(tmp_termination_msg_file):
    errors.clear_intermediate_errors()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job-ingest-iterator")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_init_fails(tmp_termination_msg_file: pathlib.Path):
    errors.clear_intermediate_errors()

    class InitFailsPlugin:
        @staticmethod
        @hookimpl
        def initialize_job(self, context: JobContext):
            raise OverflowError("Overflow")

    runner = CliEntryBasedTestRunner(InitFailsPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"


def test_run_exception_handled(tmp_termination_msg_file: pathlib.Path):
    errors.clear_intermediate_errors()

    class ExceptionHandler:
        @staticmethod
        @hookimpl
        def vdk_exception(self, exception: Exception) -> bool:
            return True

    runner = CliEntryBasedTestRunner(ExceptionHandler())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])
    cli_assert_equal(0, result)


def test_run_job_plugin_fails(tmp_termination_msg_file):
    errors.clear_intermediate_errors()

    class RunJobFailsPlugin:
        @staticmethod
        @hookimpl()
        def run_job(context: JobContext) -> None:
            raise OverflowError("Overflow")

    runner = CliEntryBasedTestRunner(RunJobFailsPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"


def test_run_platform_error_properties(tmp_termination_msg_file):
    errors.clear_intermediate_errors()

    class FailingPropertiesServiceClient(IPropertiesServiceClient):
        def read_properties(self, job_name: str, team_name: str) -> Dict:
            raise OSError("fake read error")

        def write_properties(
            self, job_name: str, team_name: str, properties: Dict
        ) -> None:
            raise OSError("fake write error")

    props_plugin = TestPropertiesPlugin()
    props_plugin.properties_client = FailingPropertiesServiceClient()

    runner = CliEntryBasedTestRunner(props_plugin)
    runner.clear_default_plugins()

    result: Result = runner.invoke(["run", util.job_path("fail-job-properties")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"


def test_run_platform_error_sql(tmp_termination_msg_file):
    errors.clear_intermediate_errors()

    class QueryFailingPlugin:
        @hookimpl
        def db_connection_execute_operation(execution_cursor: ExecutionCursor):
            raise OSError("Cannot execute query error for testing purposes")

    runner = CliEntryBasedTestRunner(QueryFailingPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-create-insert")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"


def _get_job_status(tmp_termination_msg_file):
    return json.loads(tmp_termination_msg_file.read_text())["status"]
