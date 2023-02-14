# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import sqlite3
from typing import cast
from typing import Optional
from unittest import mock

from click.testing import Result
from functional.run.util import job_path
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import DecoratedSqLite3MemoryDbPlugin
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryConnection
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin
from vdk.plugin.test_utils.util_plugins import TestPropertiesPlugin

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


@mock.patch.dict(os.environ, {})
def test_run_dbapi_connection_no_such_db_type():
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("vdk").setLevel(logging.INFO)
    runner = CliEntryBasedTestRunner()

    with mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY}):
        result: Result = runner.invoke(
            [
                "run",
                job_path("simple-create-insert"),
            ]
        )

        cli_assert_equal(1, result)
        assert "VdkConfigurationError" in result.output


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            job_path("simple-create-insert"),
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
            job_path("simple-create-insert-huge"),
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
            job_path("simple-create-insert"),
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
            job_path("simple-create-insert-failed"),
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
            job_path("simple-create-insert-failed"),
        ]
    )

    cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_arguments_and_sql_substitution():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            job_path("job-with-args"),
            "--arguments",
            '{"table_name": "test_table", "counter": 123}',
        ]
    )

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select * from test_table") == [("one", 123)]


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_properties_and_sql_substitution():
    db_plugin = SqLite3MemoryDbPlugin()
    props_plugin = TestPropertiesPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, props_plugin)
    runner.clear_default_plugins()

    props_plugin.properties_client.write_properties(
        "job-with-args", "team", {"table_name": "test_table_props"}
    )

    result: Result = runner.invoke(
        [
            "run",
            job_path("job-with-args"),
            "--arguments",
            '{"counter": 123}',
        ]
    )

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select * from test_table_props") == [
        ("one", 123)
    ]


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_properties_and_sql_substitution_priority_order():
    db_plugin = SqLite3MemoryDbPlugin()
    props_plugin = TestPropertiesPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, props_plugin)
    runner.clear_default_plugins()

    props_plugin.properties_client.write_properties(
        "job-with-args", "team", {"table_name": "test_table_props"}
    )

    result: Result = runner.invoke(
        [
            "run",
            job_path("job-with-args"),
            "--arguments",
            '{"table_name": "test_table_override", "counter": 123}',
        ]
    )

    cli_assert_equal(0, result)
    # we verify that test_table_override is used (over test_table_props) since arguments have higher priority
    assert db_plugin.db.execute_query("select * from test_table_override") == [
        ("one", 123)
    ]


class DbOperationTrackPlugin:
    def __init__(self):
        self.log = []

    @hookimpl(hookwrapper=True)
    def db_connection_execute_operation(
        self, execution_cursor: ExecutionCursor
    ) -> Optional[int]:
        self.log.append("start")
        out: HookCallResult
        out = yield
        self.log.append(("end", out.excinfo is None))


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection_with_execute_hook():
    db_plugin = SqLite3MemoryDbPlugin()
    db_tracker = DbOperationTrackPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, db_tracker)

    result: Result = runner.invoke(["run", job_path("simple-create-insert")])

    cli_assert_equal(0, result)
    assert db_tracker.log == [
        "start",
        ("end", True),
        "start",
        ("end", True),
        "start",
        ("end", True),
    ]


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection_failed_with_execute_hook():
    db_plugin = SqLite3MemoryDbPlugin()
    db_tracker = DbOperationTrackPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, db_tracker)

    result: Result = runner.invoke(["run", job_path("simple-create-insert-failed")])

    cli_assert_equal(1, result)
    assert db_tracker.log == [
        "start",
        ("end", True),
        "start",
        ("end", True),
        "start",
        ("end", False),
    ]


def test_run_dbapi_connection_with_execute_hook_proxies(tmpdir):
    class QueryExecutePlugin:
        @hookimpl(hookwrapper=True)
        def db_connection_execute_operation(
            self, execution_cursor: ExecutionCursor
        ) -> Optional[int]:
            # nonstandard convenience method and not part of PEP 249 standard
            # so this should be proxied to native cursor
            cast(sqlite3.Cursor, execution_cursor).executescript("select 1")
            yield
            cast(sqlite3.Cursor, execution_cursor).executescript("select 2")

    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin, QueryExecutePlugin())

    result: Result = runner.invoke(["run", job_path("simple-create-insert")])

    cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_get_managed_connection():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            job_path("pandas-job"),
        ]
    )

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select * from test_table") == [
        ("Computer", 900),
        ("Tablet", 300),
    ]
