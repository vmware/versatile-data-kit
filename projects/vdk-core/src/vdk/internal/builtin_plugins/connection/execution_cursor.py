# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any

from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.connection.proxy_cursor import ProxyCursor


class ExecuteOperationResult:
    def __init__(self, native_result: Any):
        self.__native_result = native_result

    def get_native_result(self) -> Any:
        """
        Returns the result of PEP249Cursor.execute invocation using the native cursor.
        Since this is vendor specific the result type is any - but usually it's number of selected or updated rows.
        :return: Any
        """
        return self.__native_result


class ExecutionCursor(ProxyCursor):
    """
    Extends ProxyCursor to provide:
        * ability to directly access and execute operations with the native cursor.
        Generally it is not execpted to be used. Perhaps only if default implementation does not work (which should be almost never)
        But it's useful to be exposed in case the native library used provide some extra features.
        For example Impala (impyla driver) provides a way to get the profile of a query after it's executed
        which can be printed to aid debugging.
        * Give access to the result of execute operation (through) ExecuteOperationResult which is vendor specific.

    See connection_hook_spec#db_connection_execute_operation for more details and examples how to use it.
    """

    def __init__(
        self,
        native_cursor: PEP249Cursor,
        managed_operation: ManagedOperation,
        log=logging.getLogger(__name__),
    ):
        super().__init__(native_cursor, log)
        self.__managed_operation = managed_operation
        self.__native_cursor = native_cursor

    def get_managed_operation(self) -> ManagedOperation:
        """
        Retrieve an object that contains information about the query and query parameters used in
        the database operation. The retrieved Data Transfer Object (DTO) is purposed
        to curate the query and parameters.

        :return: ManagedOperation
            Query and parameters DTO
        """
        return self.__managed_operation
