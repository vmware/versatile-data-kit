# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import Optional

from vdk.api.plugin.hook_markers import hookspec
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
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
    def db_connection_decorate_operation(
        self, decoration_cursor: DecorationCursor
    ) -> None:
        """
        Curates the operation and parameters.
        If an exception is raised, the cursor execution will be suspended.

        For example:
        @hookimpl
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

    @hookspec
    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        """
        Recovers the operation initiated. Retries made number is auto-incremented.
        If no exception is raised, cursor is considered successfully executed.

        For example:
        @hookimpl
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
