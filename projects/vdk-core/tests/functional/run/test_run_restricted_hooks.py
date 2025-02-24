# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from unittest import mock

from click.testing import Result
from functional.run.util import job_path
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryConnection

log = logging.getLogger(__name__)

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"


class BeforeOperationSqLite3MemoryDbPlugin:
    def new_connection(self) -> PEP249Connection:
        return SqLite3MemoryConnection()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.new_connection
        )

    @hookimpl(trylast=True)
    def db_connection_before_operation(self, operation: ManagedOperation):
        log.info(f"{operation.get_operation()} was changed")


class OperationFailureSqLite3MemoryDbPlugin:
    def __init__(self):
        self._counter = 1

    def new_connection(self) -> PEP249Connection:
        class SqliteConnection(ManagedConnectionBase):
            def get_managed_connection(self):
                return SqLite3MemoryConnection()

            def _connect(self):
                return SqLite3MemoryConnection().connect()

            def db_connection_recover_operation(
                self, recovery_cursor: RecoveryCursor
            ) -> None:
                log.info("Recovering over here, boss")

        return SqliteConnection()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.new_connection
        )

    @hookimpl
    def db_connection_before_operation(self, operation: ManagedOperation):
        if "INSERT INTO" in operation.get_operation():
            operation.set_operation(
                f"-- count: {self._counter}\n {operation.get_operation()}"
            )
            self._counter += 1

    @hookimpl(trylast=True)
    def db_connection_on_operation_failure(
        self, operation: ManagedOperation, exception: Exception
    ) -> None:
        log.info(f"Operation {operation.get_operation()} went horribly wrong")
        log.exception(exception)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_before_operation_hook():
    db_plugin = BeforeOperationSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            job_path("simple-create-insert"),
        ]
    )

    cli_assert_equal(0, result)
    expected = (
        "CREATE TABLE stocks\n"
        "        (date text, symbol text, price real)\n"
        " was changed\n"
    )
    assert expected in result.output


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_on_failure_hook():
    db_plugin = OperationFailureSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            job_path("simple-create-insert-failed"),
        ]
    )

    cli_assert_equal(0, result)

    # Check if the on_failure hook was called
    expected_on_failure = (
        "INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', Syntax error )\n"
        " went horribly wrong\n"
    )

    expected_exception_on_failure = 'near "error": syntax error'

    assert expected_on_failure in result.output
    assert expected_exception_on_failure in result.output

    # Make sure the before hook was called for the on-failure operation
    expected_before = "Operation -- count: 2"
    assert expected_before in result.output
