# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
import sqlite3
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.errors import VdkConfigurationError
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import DecoratedSqLite3MemoryDbPlugin
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryConnection
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin

log = logging.getLogger(__name__)

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"


class ValidatedSqLite3MemoryDbPlugin:
    def new_connection(self) -> PEP249Connection:
        return SqLite3MemoryConnection()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.new_connection
        )

    @hookimpl(trylast=True)
    def db_connection_validate_operation(self, operation, parameters):
        parameters_length = 0
        if parameters:
            parameters_length = len("".join(map(str, parameters)))

        if len(operation) + parameters_length > 10000:
            raise Exception(
                "Database operation has exceeded the maximum limit of 10000 characters."
            )


class SyntaxErrorRecoverySqLite3MemoryDbPlugin:
    def __init__(self):
        self._max_retries = 5

    def new_connection(self) -> PEP249Connection:
        return SqLite3MemoryConnection()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.new_connection
        )

    @hookimpl(trylast=True)
    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        managed_operation = recovery_cursor.get_managed_operation()
        if "syntax error".upper() in recovery_cursor.get_exception().args[0].upper():
            recovery_cursor.execute(
                managed_operation.get_operation().replace("Syntax error", "123.0")
            )
            recovery_cursor.retries_increment()


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection_no_such_db_type():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(
        [
            "run",
            util.job_path("simple-create-insert"),
        ]
    )

    cli_assert_equal(1, result)
    assert isinstance(result.exception, VdkConfigurationError)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert",
            ),
        ]
    )

    cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_managed_connection_and_verify_query_length():
    db_plugin = ValidatedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert-huge",
            ),
        ]
    )

    cli_assert_equal(1, result)
    assert (
            "Database operation has exceeded the maximum limit of 10000 characters."
            == result.exception.args[0]
    )


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_managed_connection_and_check_query_comments():
    db_plugin = DecoratedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert",
            ),
        ]
    )

    cli_assert_equal(0, result)
    assert len(db_plugin.statements_history) == 3
    # assert those are automatically added as comments
    assert all(
        ["-- op_id" in statement for statement in db_plugin.statements_history]
    ), f"op_id missing: {db_plugin.statements_history}"
    assert all(
        ["-- job_name" in statement for statement in db_plugin.statements_history]
    ), f"job name missing: {db_plugin.statements_history}"


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_managed_connection_and_query_fails():
    db_plugin = DecoratedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert-failed",
            ),
        ]
    )

    cli_assert_equal(1, result)
    assert isinstance(result.exception, sqlite3.OperationalError)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_managed_connection_and_query_fails_then_recovers():
    db_plugin = SyntaxErrorRecoverySqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert-failed",
            ),
        ]
    )

    cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_arguments():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "job-with-args",
            ),
            "--arguments",
            '{"table_name": "test_table", "counter": 123}',
        ]
    )

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select * from test_table") == [("one", 123)]
