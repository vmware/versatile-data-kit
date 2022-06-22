# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import cast

from vdk.api.plugin.connection_hook_spec import ConnectionHookSpec
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.execution_cursor import (
    ExecuteOperationResult,
)
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import PlatformServiceError


class DefaultConnectionHookImpl:
    """
    The default implementation of execute operation.
    Generally it should not be overridden.
    To "override" with new implementation, make a new hook which returns non-None ExecuteOperationResult.
    See ConnectionHookSpec documentation for more details.
    """

    @hookimpl(trylast=True)
    def db_connection_execute_operation(self, execution_cursor: ExecutionCursor) -> Any:
        managed_operation = execution_cursor.get_managed_operation()
        if managed_operation.get_parameters():
            native_result = execution_cursor.execute(
                managed_operation.get_operation(), managed_operation.get_parameters()
            )
        else:
            native_result = execution_cursor.execute(managed_operation.get_operation())
        return ExecuteOperationResult(native_result)


class ConnectionHookSpecFactory:
    """
    Class used to create properly initialized ConnectionHookSpec instance to use to execute the underlying hooks
    """

    def __init__(self, plugin_registry: IPluginRegistry):
        self.__plugin_registry = plugin_registry

    def get_connection_hook_spec(self) -> ConnectionHookSpec:
        """
        Returns ConnectionHookSpec class which would act as a relay and invoke the underlying implemented hooks
        It's generally a ConnectionHookSpec cast of plugin_registry.PluginHookRelay to enable easier hook invocations.
        It also initializes some of the hooks (now only db_connection_execute_operation) with default implementations.
        :return: ConnectionHookSpec
        """
        if self.__plugin_registry:
            if not self.__plugin_registry.has_plugin(
                DefaultConnectionHookImpl.__name__
            ):
                self.__plugin_registry.load_plugin_with_hooks_impl(
                    DefaultConnectionHookImpl(), DefaultConnectionHookImpl.__name__
                )
            return cast(ConnectionHookSpec, self.__plugin_registry.hook())
        else:
            raise PlatformServiceError(
                ErrorMessage(
                    "Managed Cursor not initialized properly",
                    "Cannot connect to database using vdk managed cursor",
                    "Plugin registry is not initialized. That seems like a bug.",
                    "Without plugin registry the connection cannot be started",
                    "Open a vdk github issue "
                    "and/or revert to previous version of vdk-core.",
                )
            )
