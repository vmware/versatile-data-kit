# Copyright 2021-2023 VMware, Inc.
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
from vdk.api.plugin.plugin_input import ISecretsServiceClient
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableByActual
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin
from vdk.plugin.test_utils.util_plugins import TestPropertiesPlugin
from vdk.plugin.test_utils.util_plugins import TestSecretsPlugin

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"


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
    errors.resolvable_context().clear()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("syntax-error-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_user_error(tmp_termination_msg_file):
    errors.resolvable_context().clear()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"

    assert errors.get_blamee_overall() == ResolvableByActual.USER
    actual_error = errors.resolvable_context().resolvables.get(ResolvableByActual.USER)[
        0
    ]
    assert actual_error.resolved is False


def test_run_user_error_fail_job_library(tmp_termination_msg_file):
    errors.resolvable_context().clear()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job-indirect-library")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_user_error_fail_job_ingest_iterator(tmp_termination_msg_file):
    errors.resolvable_context().clear()
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("fail-job-ingest-iterator")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "User error"


def test_run_init_fails(tmp_termination_msg_file: pathlib.Path):
    errors.resolvable_context().clear()

    class InitFailsPlugin:
        @staticmethod
        @hookimpl
        def initialize_job(self, context: JobContext):
            raise OverflowError("Overflow")

    runner = CliEntryBasedTestRunner(InitFailsPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"

    assert errors.get_blamee_overall() == ResolvableByActual.PLATFORM
    actual_error = errors.resolvable_context().resolvables.get(
        ResolvableByActual.PLATFORM
    )[0]
    assert actual_error.resolved is False


def test_run_exception_handled(tmp_termination_msg_file: pathlib.Path):
    errors.resolvable_context().clear()

    class ExceptionHandler:
        @staticmethod
        @hookimpl
        def vdk_exception(self, exception: Exception) -> bool:
            return True

    runner = CliEntryBasedTestRunner(ExceptionHandler())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])
    cli_assert_equal(0, result)


def test_run_job_plugin_fails(tmp_termination_msg_file):
    errors.resolvable_context().clear()

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
    errors.resolvable_context().clear()

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


def test_run_platform_error_secrets(tmp_termination_msg_file):
    errors.resolvable_context().clear()

    class FailingSecretsServiceClient(ISecretsServiceClient):
        def read_secrets(self, job_name: str, team_name: str) -> Dict:
            raise OSError("fake read error")

        def write_secrets(self, job_name: str, team_name: str, secrets: Dict) -> None:
            raise OSError("fake write error")

    secrets_plugin = TestSecretsPlugin()
    secrets_plugin.secrets_client = FailingSecretsServiceClient()

    runner = CliEntryBasedTestRunner(secrets_plugin)
    runner.clear_default_plugins()

    result: Result = runner.invoke(["run", util.job_path("fail-job-secrets")])
    cli_assert_equal(1, result)
    assert _get_job_status(tmp_termination_msg_file) == "Platform error"


def test_run_platform_error_sql(tmp_termination_msg_file):
    errors.resolvable_context().clear()

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


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_user_error_handled(tmp_termination_msg_file):
    errors.resolvable_context().clear()
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        ["run", util.job_path("simple-query-failed-handled")]
    )
    cli_assert_equal(0, result)
    assert (json.loads(tmp_termination_msg_file.read_text())["status"]) == "Success"
