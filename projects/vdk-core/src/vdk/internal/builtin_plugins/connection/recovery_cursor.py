# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class OperationRecovery:
    def __init__(self, exception, managed_operation: ManagedOperation):
        self.__exception = exception
        self.__managed_operation = managed_operation
        self.__retries = 0

    def get_exception(self):
        return self.__exception

    def get_managed_operation(self):
        return self.__managed_operation

    def get_retries(self):
        return self.__retries

    def retries_increment(self):
        self.__retries += 1

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, OperationRecovery):
            return False
        return (
            self.__operation == o.get_operation()
            and self.__parameters == o.get_parameters()
        )

    def __hash__(self) -> int:
        return hash((self.__operation, self.__parameters))


class RecoveryCursor(PEP249Cursor):
    def __init__(
        self,
        native_cursor: PEP249Cursor,
        log,
        operation_recovery: OperationRecovery,
        decoration_cursor: DecorationCursor,
        decoration_operation_callback,
    ):
        super().__init__(native_cursor, log)
        self.__operation_recovery = operation_recovery
        self.__decoration_cursor = decoration_cursor
        self.__decoration_operation_callback = decoration_operation_callback

    def get_operation_recovery(self) -> OperationRecovery:
        return self.__operation_recovery

    def get_retries(self) -> int:
        return self.__operation_recovery.get_retries()

    def execute(self, operation, parameters=None):
        """
        Execute an additional query purposed for the recovery of the original operation.

        :param operation: helper query to facilitate operation recovery
        :param parameters: helper query parameters
        """
        managed_operation = ManagedOperation(operation, parameters)
        if self.__decoration_operation_callback:
            self._log.debug("Before executing recovery query:\n%s" % operation)
            self.__decoration_operation_callback(
                decoration_cursor=self.__decoration_cursor,
                managed_operation=managed_operation,
            )

        self._log.info(
            "Executing recovery query:\n%s"
            % managed_operation.get_operation_decorated()
        )
        try:
            super().execute(*managed_operation.get_decorated())
            self._log.info("Executing recovery query SUCCEEDED.")
        except Exception as e:
            self.__operation_recovery.retries_increment()
            self._log.warning("Executing recovery query FAILED.", e)
            raise e

    def retry_operation(self):
        """
        Retry original operation to recover.
        """
        # could potentially enforce max retries here globally - in favour of per custom error handler
        operation_recovery = self.__operation_recovery
        operation_recovery.retries_increment()

        retry_number = operation_recovery.get_retries()

        self._log.info(
            f"Retrying attempt #{retry_number} "
            f"for query:\n{operation_recovery.get_managed_operation().get_operation_decorated()}"
        )
        try:
            super().execute(*operation_recovery.get_managed_operation().get_decorated())
            self._log.info(f"Retrying attempt #{retry_number} for query SUCCEEDED.")
        except Exception as e:
            self._log.warning(f"Retrying attempt #{retry_number} for query FAILED.", e)
            raise e
