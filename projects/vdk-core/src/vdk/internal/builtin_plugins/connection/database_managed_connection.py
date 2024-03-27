# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import Optional

from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.execution_cursor import (
    ExecuteOperationResult,
)
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor


class IDatabaseManagedConnection:
    def db_connection_validate_operation(
        self, operation: str, parameters: Optional[Container]
    ) -> None:
        """
        Validates the query and parameters.

        For example:
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

    def db_connection_decorate_operation(
        self, decoration_cursor: DecorationCursor
    ) -> None:
        """
        Curates the operation and parameters.
        If an exception is raised, the cursor execution will be suspended.

        For example:
        db_connection_decorate_operation(decoration_cursor: DecorationCursor):
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation("prefix" +
                                            managed_operation.get_operation())

        :param decoration_cursor: DecorationCursor
            A PEP249Cursor implementation purposed for query and parameters decoration.
            Provides operation details and tooling.
        :return:
        """
        pass

    def db_connection_execute_operation(
        self, execution_cursor: ExecutionCursor
    ) -> Optional[ExecuteOperationResult]:
        """
        The method that executes the actual SQL query using execution cursor.
        For example: let's say we are writing vdk-impala plugin and want to print more debug info
            which is available from the Impala native cursor (provided by impyla library)
                db_connection_execute_operation(execution_cursor: ExecutionCursor) -> Optional[int]:
                    yield # let the query execute first
                    c = cast(impala.interface.Cursor, execution_cursor)
                    log.info(f"Query {execution_cursor.get_managed_operation().get_operation()} debug info:"
                            f"summary: {c.get_summary()}, profile: {c.get_profile()}")
        :param execution_cursor: ExecutionCursor
        A PEP249Cursor implementation purposed for actual query execution.
        """
        managed_operation = execution_cursor.get_managed_operation()
        if managed_operation.get_parameters():
            native_result = execution_cursor.execute(
                managed_operation.get_operation(), managed_operation.get_parameters()
            )
        else:
            native_result = execution_cursor.execute(managed_operation.get_operation())
        return ExecuteOperationResult(native_result)

    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        """
        Recovers the operation initiated. Retries made number is auto-incremented.
        If no exception is raised, cursor is considered successfully executed.

        For example:
        db_connection_recover_operation(recovery_cursor: RecoveryCursor):
            while recovery_cursor.get_retries() < MAX_RETRIES:
                try:
                    recovery_cursor.execute("helper query")
                    recovery_cursor.retry_operation()
                    return
                except:
                    time.sleep(3 * recovery_cursor.get_retries()) # backoff
            raise recovery_cursor.get_exception()

        :param recovery_cursor: RecoveryCursor
            A PEP249Cursor implementation purposed for query and parameters recovery.
            Provides operation details and tooling.
        :return:
        """
        pass

    def db_connection_after_operation(self, execution_cursor: ExecutionCursor) -> None:
        """
        This method runs after the execution of the database operation.
        It can be used for tasks such as auditing, logging, cleanup, or additional validations.

        For example:
        db_connection_after_operation(post_operation_cursor):
             hive_cursor = cast(HiveServer2Cursor, execution_cursor)
             lineage_data = self._get_lineage_data(hive_cursor)
             if (lineage_data):
                    lineage_logger.send(lineage_data)

        :param execution_cursor: ExecutionCursor
        :return:
        """
        pass
