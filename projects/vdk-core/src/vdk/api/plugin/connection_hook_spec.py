# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import Optional

from vdk.api.plugin.hook_markers import hookspec
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.execution_cursor import (
    ExecuteOperationResult,
)
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor


class ConnectionHookSpec:
    """
    These are hook specifications that enable plugins to hook
        at PEP249Connection and PEP249Cursor events during execution.
    Sequence of evaluation:
        1. db_connection_validate_operation
        2. db_connection_decorate_operation
        * cursor is executed
            ** in case of recovery needed -> db_connection_recover_operation

    Use Cases
        db_connection_validate_operation: if valid return  else raise exception
        db_connection_decorate_operation: ..set_operation( prefix + operation)
        db_connection_recover_operation: ..get_retries()..retry_operation()..
    """

    @hookspec
    def db_connection_validate_operation(
        self, operation: str, parameters: Optional[Container]
    ) -> None:
        """
        Validates the query and parameters.

        For example:
        @hookimpl
        db_connection_validate_operation(operation, parameters):
            if(_max_query_length_limit_exceeded(operation, parameters)):
                raise Exception("max query length limit exceeded")

        :param operation: str
            Database operation - a SQL query or command to be executed.
        :param parameters: Optional[Container]
            Parameters may be provided as sequence or mapping and will be bound to variables in the operation.
            Variables are specified in a database-specific notation. See chosen database documentation for details.
        :return:
        """
        pass

    @hookspec
    def db_connection_before_operation(self, operation: ManagedOperation) -> None:
        """
        Curates the operation and parameters.
        If an exception is raised, the cursor execution will be suspended.

        For example:
        @hookimpl
        db_connection_decorate_operation_restrictive(managed_operation: ManagedOperation):
            managed_operation.set_operation("prefix" +
                                             managed_operation.get_operation())

        :param operation: ManagedOperation
            ManagedOperation object. Provides the operation (usually an SQL expression and some metadata)
        :return:
        """
        pass

    @hookspec
    def db_connection_on_operation_failure(
        self, operation: ManagedOperation, exception: Exception
    ) -> None:
        """
        Executes if a database operation fails. Gives the caller a chance to log the error,
        send metrics or otherwise take action on failure.

        For example:
        @hookimpl
        db_connection_on_operation_failure(operation: ManagedOperation):
            log.error(f"Query {operation.get_operation()} failed. Reporting the incident...")
            metrics_api.report(operation.get_operation(), operation.get_parameters())

        :param operation: ManagedOperation
            ManagedOperation object. Provides the operation (usually an SQL expression and some metadata)
        :param exception: Exception
            the exception that was thrown
        :return:
        """
        pass
