# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Container
from typing import Optional
from typing import Tuple

from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class ManagedOperation:
    def __init__(self, operation: str, parameters: Optional[Container]):
        self.__operation = operation
        self.__parameters = parameters
        self.__operation_decorated = operation
        self.__parameters_decorated = parameters

    def get_initial_operation(self):
        return self.__operation

    def get_initial_parameters(self):
        return self.__parameters

    def get_operation_decorated(self):
        return self.__operation_decorated

    def get_parameters_decorated(self):
        return self.__parameters_decorated

    def get_decorated(self) -> Tuple[str, Optional[Container]]:
        return self.__operation_decorated, self.__parameters_decorated

    # maybe track modification history
    def set_operation_decorated(self, decorated_operation):
        self.__operation_decorated = decorated_operation

    def set_parameters_decorated(self, decorated_parameters):
        self.__parameters_decorated = decorated_parameters

    def set_decorated(self, decorated_operation, decorated_parameters):
        self.set_operation_decorated(decorated_operation)
        self.set_parameters_decorated(decorated_parameters)


class DecorationCursor(PEP249Cursor):
    def __init__(self, native_cursor: PEP249Cursor, log):
        super().__init__(native_cursor, log)

    def execute(self, operation, parameters=None):
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
            self._log.warning("Executing decoration query FAILED.", e)
            raise e
