# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor


class RecoveryCursor(PEP249Cursor):
    """
    Extends PEP249Cursor to provide:
        * query and parameters executed
        * exception that occurred during execution
        * tooling for operation recovery

    See connection_hook_spec#db_connection_recover_operation for more details and examples how to use it.
    """

    def __init__(
        self,
        native_cursor: PEP249Cursor,
        log,
        exception,
        managed_operation: ManagedOperation,
        decoration_operation_callback,
    ):
        super().__init__(native_cursor, log)
        self.__exception = exception
        self.__managed_operation = managed_operation
        self.__decoration_operation_callback = decoration_operation_callback
        self.__retries = 0

    def get_exception(self) -> Exception:
        """
        Retrieve the original exception with which the SQL operation failed.

        :return: Exception
        """
        return self.__exception

    def get_managed_operation(self) -> ManagedOperation:
        """
        Retrieve an object that contains information about the query and query parameters used in
        the database operation. The retrieved Data Transfer Object (DTO) is purposed
        to curate the query and parameters.

        :return: ManagedOperation
            Query and parameters DTO
        """
        return self.__managed_operation

    def get_retries(self) -> int:
        """
        Fetch retries made using retry_operation().

        :return: int
            Number of operation retries performed
        """
        return self.__retries

    def execute(self, operation, parameters=None) -> None:
        """
        Execute an additional query purposed for the recovery of the original operation.

        :param operation: helper query to facilitate operation recovery
        :param parameters: helper query parameters
        """
        managed_operation = ManagedOperation(operation, parameters)
        if self.__decoration_operation_callback:
            self._log.debug("Before executing recovery query:\n%s" % operation)
            self.__decoration_operation_callback(
                decoration_cursor=DecorationCursor(
                    self._cursor, self._log, managed_operation
                )
            )
        self._log.info(
            "Executing recovery query:\n%s" % managed_operation.get_operation()
        )
        try:
            super().execute(*managed_operation.get_operation_parameters_tuple())
            self._log.info("Executing recovery query SUCCEEDED.")
        except Exception as e:
            self.retries_increment()
            self._log.warning(f"Executing recovery query FAILED. Exception: {e}")
            raise e

    def retry_operation(self) -> None:
        """
        Retry original operation to recover.
        """
        # could potentially enforce max retries here globally - in favour of per custom error handler
        self.retries_increment()
        retry_number = self.get_retries()

        self._log.info(
            f"Retrying attempt #{retry_number} "
            f"for query:\n{self.get_managed_operation().get_operation()}"
        )
        try:
            super().execute(
                *self.get_managed_operation().get_operation_parameters_tuple()
            )
            self._log.info(f"Retrying attempt #{retry_number} for query SUCCEEDED.")
        except Exception as e:
            self._log.warning(
                f"Retrying attempt #{retry_number} for query FAILED. Exception: {e}"
            )
            raise e

    def retries_increment(self) -> None:
        self.__retries += 1
