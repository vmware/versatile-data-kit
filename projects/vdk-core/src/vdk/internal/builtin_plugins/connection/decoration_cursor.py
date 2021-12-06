# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import Optional
from typing import Tuple

from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class ManagedOperation:
    """
    An object that contains information about the query and query parameters used in the database operation.
    A Data Transfer Object or DTO.
    """

    def __init__(self, operation: str, parameters: Optional[Container]):
        self.__operation = operation
        self.__parameters = parameters
        self.__operation_decorated = operation
        self.__parameters_decorated = parameters

    def get_initial_operation(self) -> str:
        """
        The initial operation (usually SQL expression) before being modified by any plugin.
        :return: str
        """
        return self.__operation

    def get_initial_parameters(self) -> Optional[Container]:
        """
        The initial parameters before being modified by any plugin.
        :return: Optional[Container]
        """
        return self.__parameters

    def get_operation(self) -> str:
        """
        The operation (usually SQL expression) that is expected to be executed.
        It may have been modified by other plugins.
        :return: str
        """
        return self.__operation_decorated

    def get_parameters(self) -> Optional[Container]:
        """
        The parameters that are expected to be used during operation execution.
        It may have been modified by other plugins.
        :return: Optional[Container]
        """
        return self.__parameters_decorated

    def get_operation_parameters_tuple(self) -> Tuple[str, Optional[Container]]:
        """
        The operation (usually SQL expression) and parameters that is expected to be executed.
        They may have been modified by other plugins.
        :return: Tuple[str, Optional[Container]]
        """
        return self.__operation_decorated, self.__parameters_decorated

    # maybe track modification history
    def set_operation(self, decorated_operation: str):
        """
        Set the active operation that will be executed. Use it to decorate or change the operation (or SQL expression).
        :param decorated_operation: str
            The operation modified
        :return:
        """
        self.__operation_decorated = decorated_operation

    def set_parameters(self, decorated_parameters: Optional[Container]):
        """
        Set the active parameters that will be used during operation execution.
        Use it to decorate or change the parameters.
        :param decorated_parameters: Optional[Container]
            The parameters modified
        :return:
        """
        self.__parameters_decorated = decorated_parameters

    def set_operation_parameters_tuple(
        self, decorated_operation: str, decorated_parameters: Optional[Container]
    ):
        """
        Set the active operation and parameters that will be executed.
        Use it to decorate or change the operation (or SQL expression) and parameters.
        :param decorated_operation: str
        :param decorated_parameters: Optional[Container]
        :return:
        """
        self.set_operation(decorated_operation)
        self.set_parameters(decorated_parameters)


class DecorationCursor(PEP249Cursor):
    """
    Extends PEP249Cursor to provide:
        * query and parameters to be executed
        * tooling for curating the operation
        * tooling for pre-executing other decorative queries
    """

    def __init__(
        self, native_cursor: PEP249Cursor, log, managed_operation: ManagedOperation
    ):
        super().__init__(native_cursor, log)
        self.__managed_operation = managed_operation

    def get_managed_operation(self) -> ManagedOperation:
        """
        Retrieve operation DTO to curate the query and parameters.

        :return: ManagedOperation
            Query and parameters DTO
        """
        return self.__managed_operation

    def execute(self, operation, parameters=None) -> None:
        """
        Execute an additional query purposed for decoration of the original operation.

        :param operation: decoration query
        :param parameters: decoration query parameters
        """
        self._log.info(f"Executing decoration query:\n{operation}")
        try:
            super().execute(operation, parameters)
            self._log.info("Executing decoration query SUCCEEDED.")
        except Exception as e:
            self._log.warning(f"Executing decoration query FAILED. Exception: {e}")
            raise e
