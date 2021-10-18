# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import List
from typing import Optional
from typing import Tuple

import click
from vdk.api.plugin.hook_markers import hookspec
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext


class ConnectionHookSpec:
    """
    These are hook specifications that enable plugins to hook
        at PEP249Connection and PEP249Cursor events during execution.
    Sequence of evaluation:
        1. validate_operation
        2. decorate_operation
        * cursor is executed
            ** in case of recovery needed -> recover_operation

    Use Cases
        validate_operation: if valid return  else raise exception
        decorate_operation: ..set_operation( prefix + operation)
        recover_operation: ..get_retries()..retry_operation()..
    """

    @hookspec
    def validate_operation(
        self, operation: str, parameters: Optional[Container]
    ) -> None:
        """
        Validates the query and parameters.

        E.g.
        @hookimpl
        validate_operation(operation, parameters):
            if(_max_query_length_limit_exceeded(operation, parameters)):
                raise Exception("max query length limit exceeded")

        :param operation: str
            Query
        :param parameters: Optional[Container]
            Query parameters
        :return:
        """
        pass

    @hookspec
    def decorate_operation(self, decoration_cursor: DecorationCursor) -> None:
        """
        Curates the operation and parameters.
        If an exception is raised, the cursor execution will be suspended.

        E.g.
        @hookimpl
        decorate_operation(decoration_cursor: DecorationCursor):
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation("prefix" +
                                             managed_operation.get_operation())

        :param decoration_cursor: DecorationCursor
            A PEP249Cursor implementation purposed for query and parameters decoration.
            Provides operation details and tooling.
        :param managed_operation: ManagedOperation
            Query and parameters DTO
        :return:
        """
        pass

    @hookspec
    def recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        """
        Recovers the operation initiated. Retries made number is auto-incremented.
        If no exception is raised, cursor is considered successfully executed.

        E.g.
        @hookimpl
        recover_operation(recovery_cursor: RecoveryCursor):
            while(recovery_cursor.get_retries() < MAX_RETRIES):
                try:
                    recovery_cursor.execute("helper query")
                    recovery_cursor.retry_operation()
                except:
                    time.sleep(3 * recovery_cursor.get_retries()) # backoff

        :param recovery_cursor: RecoveryCursor
            A PEP249Cursor implementation purposed for query and parameters recovery.
            Provides operation details and tooling.
        :return:
        """
        pass
