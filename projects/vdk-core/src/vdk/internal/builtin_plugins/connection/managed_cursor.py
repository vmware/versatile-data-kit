# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import types
from datetime import timedelta
from timeit import default_timer as timer
from typing import Any
from typing import cast
from typing import Collection
from typing import Container
from typing import Optional

from vdk.internal.builtin_plugins.connection.connection_hooks import (
    ConnectionHookSpecFactory,
)
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    DefaultConnectionHookImpl,
)
from vdk.internal.builtin_plugins.connection.database_managed_connection import (
    IDatabaseManagedConnection,
)
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.proxy_cursor import ProxyCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core import errors


class ManagedCursor(ProxyCursor):
    """
    PEP249 Managed Cursor. It takes and sits on the control and data path of SQL queries and client.
    """

    def __init__(
        self,
        cursor: Any,
        log: logging.Logger = None,
        connection_hook_spec_factory: ConnectionHookSpecFactory = None,
        managed_database_connection: IDatabaseManagedConnection = None,
    ):
        if not log:
            log = logging.getLogger(__name__)
        super().__init__(cursor, log)
        self.__connection_hook_spec = None
        if connection_hook_spec_factory:
            self.__connection_hook_spec = (
                connection_hook_spec_factory.get_connection_hook_spec()
            )

        self.__managed_database_connection = managed_database_connection

    def __getattr__(self, attr):
        """
        Dynamic interception and il of any (non-overridden) attribute access.
        In case an attribute is not explicitly managed (customized by overriding e.g. execute()) -
        this attribute is looked up then the call is delegated, ensuring default behaviour success path.

        First, the non-managed attribute call is redirected to the wrapped native cursor if attribute available,
        otherwise to the superclass if attribute is present.
        If the attribute is not specified by both the native cursor nor the superclass, an AttributeError is raised.

        Default behaviour availability unblocks various ManagedCursor usages that rely on
        currently not explicitly defined in the scope of ManagedCursor attributes.
        E.g. SQLAlchemy dependency that uses the ManagedCursor, does require some specific attributes available.

        For more details on customizing attributes access, see PEP562.
        """
        # native cursor
        if hasattr(self._cursor, attr):
            if isinstance(getattr(self._cursor, attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(self._cursor, attr)(*args, **kwargs)

                return method
            return getattr(self._cursor, attr)
        # superclass
        if hasattr(super(), attr):
            if isinstance(getattr(super(), attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(super(), attr)(*args, **kwargs)

                return method
            return getattr(super(), attr)
        raise AttributeError

    def execute(
        self, operation: str, parameters: Optional[Container] = None
    ) -> None:  # @UnusedVariable
        managed_operation, decoration_cursor = (
            ManagedOperation(operation, parameters),
            None,
        )
        if self.__connection_hook_spec or self.__managed_database_connection:
            self._validate_operation(operation, parameters)
            self._decorate_operation(managed_operation, operation)

        query_start_time = timer()
        try:
            result = self._execute_operation(managed_operation)
            self._log.info(
                f"Executing query SUCCEEDED. Query {_get_query_duration(query_start_time)}"
            )
            self._after_operation(managed_operation)
            return result
        except Exception as e:
            try:
                self._recover_operation(e, managed_operation)
                self._log.info(
                    f"Recovered query {_get_query_duration(query_start_time)}"
                )
            except Exception as e:
                blamee = errors.ResolvableBy.USER_ERROR
                self._log.info(f"Failed query {_get_query_duration(query_start_time)}")
                self._log.error(
                    "\n".join(
                        [
                            "Executing query FAILED.",
                            errors.MSG_WHY_FROM_EXCEPTION(e),
                        ]
                    )
                )
                errors.report(
                    blamee,
                    e,
                )
                raise e

    def _decorate_operation(self, managed_operation: ManagedOperation, operation: str):
        decorate_operation = None

        # Check if database decorate operation is overridden by a plugin.
        # Use the overridden method if available.
        # Otherwise, verify the presence of hooks; if absent, use the default hook implementation.
        if (
            self.__managed_database_connection
            and type(
                self.__managed_database_connection
            ).db_connection_decorate_operation
            != IDatabaseManagedConnection.db_connection_decorate_operation
        ):
            decorate_operation = (
                self.__managed_database_connection.db_connection_decorate_operation
            )

        elif (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_decorate_operation.get_hookimpls()
        ):
            decorate_operation = (
                self.__connection_hook_spec.db_connection_decorate_operation
            )

        # apply any changes @hookimpls to the managed operation
        if (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_before_operation.get_hookimpls()
        ):
            self.__connection_hook_spec.db_connection_before_operation(
                operation=managed_operation
            )

        if decorate_operation:
            self._log.debug("Decorating query:\n%s" % operation)
            decoration_cursor = DecorationCursor(
                self._cursor, self._log, managed_operation
            )
            try:
                decorate_operation(decoration_cursor=decoration_cursor)
            except Exception as e:
                self._log.error(
                    "\n".join(
                        [
                            "Decorating query FAILED.",
                            errors.MSG_WHY_FROM_EXCEPTION(e),
                        ]
                    )
                )
                errors.report(errors.ResolvableBy.PLATFORM_ERROR, e)
                raise e

    def _validate_operation(self, operation: str, parameters: Optional[Container]):
        validate_operation = None

        # Check if database validate operation is overridden by a plugin.
        # Use the overridden method if available.
        # Otherwise, verify the presence of hooks; if absent, use the default hook implementation.
        if (
            self.__managed_database_connection
            and type(
                self.__managed_database_connection
            ).db_connection_validate_operation
            != IDatabaseManagedConnection.db_connection_validate_operation
        ):
            validate_operation = (
                self.__managed_database_connection.db_connection_validate_operation
            )

        elif (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_validate_operation.get_hookimpls()
        ):
            validate_operation = (
                self.__connection_hook_spec.db_connection_validate_operation
            )

        if validate_operation:
            self._log.debug("Validating query:\n%s" % operation)
            try:
                validate_operation(operation=operation, parameters=parameters)
            except Exception as e:
                self._log.error(
                    "\n".join(
                        [
                            "Validating query FAILED.",
                            errors.MSG_WHY_FROM_EXCEPTION(e),
                        ]
                    )
                )
                errors.report(
                    errors.ResolvableBy.USER_ERROR,
                    exception=e,
                )
                raise e

    def _execute_operation(self, managed_operation: ManagedOperation):
        self._log.info("Executing query:\n%s" % managed_operation.get_operation())
        execution_cursor = ExecutionCursor(self._cursor, managed_operation, self._log)

        # Check if database execute operation is overridden by a plugin.
        # Use the overridden method if available.
        # Otherwise, verify the presence of hooks; if absent, use the default hook implementation.
        if (
            self.__managed_database_connection
            and type(self.__managed_database_connection).db_connection_execute_operation
            != IDatabaseManagedConnection.db_connection_execute_operation
        ):
            result = self.__managed_database_connection.db_connection_execute_operation(
                execution_cursor=execution_cursor
            )

        elif self.__connection_hook_spec:
            result = self.__connection_hook_spec.db_connection_execute_operation(
                execution_cursor=execution_cursor
            )
        else:
            self._log.debug(
                "No connection hook spec defined. "
                "Will invoke standard cursor execute implementation."
            )
            result = DefaultConnectionHookImpl().db_connection_execute_operation(
                execution_cursor
            )
        return result

    def _after_operation(self, managed_operation: ManagedOperation):
        execution_cursor = ExecutionCursor(self._cursor, managed_operation, self._log)

        if (
            self.__managed_database_connection
            and self.__managed_database_connection.db_connection_after_operation
        ):
            try:
                self._log.debug(
                    "Executing after operation:\n%s" % managed_operation.get_operation()
                )
                self.__managed_database_connection.db_connection_after_operation(
                    execution_cursor=execution_cursor
                )
            except Exception as e:
                self._log.error(
                    "\n".join(
                        [
                            "After query FAILED.",
                            errors.MSG_WHY_FROM_EXCEPTION(e),
                        ]
                    )
                )
                errors.report(
                    errors.ResolvableBy.USER_ERROR,
                    exception=e,
                )
                raise e

    def fetchall(self) -> Collection[Collection[Any]]:
        self._log.info("Fetching all results from query ...")
        try:
            res = self._cursor.fetchall()
            self._log.info("Fetching all results from query SUCCEEDED.")
            return cast(Collection[Collection[Any]], res)
        except:
            self._log.info("Fetching all results from query FAILED.")
            raise

    def close(self) -> None:
        self._log.info("Closing DB cursor ...")
        self._cursor.close()
        self._log.info("Closing DB cursor SUCCEEDED.")

    def _recover_operation(self, exception, managed_operation):
        # TODO: configurable generic re-try.

        # Check if database recover and decorate operations are overridden by a plugin.
        # Use the overridden methods if available.
        # Otherwise, verify the presence of hooks; if absent, use the default hook implementation.

        available_recovery_plugin_implementation = (
            self.__managed_database_connection
            and (
                type(self.__managed_database_connection).db_connection_recover_operation
                != IDatabaseManagedConnection.db_connection_recover_operation
            )
        )

        available_decoration_plugin_implementation = (
            self.__managed_database_connection
            and type(
                self.__managed_database_connection
            ).db_connection_decorate_operation
            != IDatabaseManagedConnection.db_connection_decorate_operation
        )

        if (
            not self.__connection_hook_spec
            or not self.__connection_hook_spec.db_connection_recover_operation.get_hookimpls()
        ) and not available_recovery_plugin_implementation:
            raise exception

        if available_decoration_plugin_implementation:
            decorate_operation = (
                self.__managed_database_connection.db_connection_decorate_operation
            )
        elif (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_decorate_operation.get_hookimpls()
        ):
            decorate_operation = (
                self.__connection_hook_spec.db_connection_decorate_operation
            )
        else:
            decorate_operation = None

        if available_recovery_plugin_implementation:
            recover_operation = (
                self.__managed_database_connection.db_connection_recover_operation
            )
        else:
            recover_operation = (
                self.__connection_hook_spec.db_connection_recover_operation
            )

        # apply any changes from @hookimpls to the managed operation
        if (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_before_operation.get_hookimpls()
        ):
            self.__connection_hook_spec.db_connection_before_operation(
                operation=managed_operation
            )

        # apply any changes from @hookimpls to the managed operation
        if (
            self.__connection_hook_spec
            and self.__connection_hook_spec.db_connection_on_operation_failure.get_hookimpls()
        ):
            self.__connection_hook_spec.db_connection_on_operation_failure(
                operation=managed_operation
            )

        recovery_cursor = RecoveryCursor(
            self._cursor,
            self._log,
            exception,
            managed_operation,
            decorate_operation,
        )
        self._log.debug(f"Recovery of query {managed_operation.get_operation()}")
        try:
            recover_operation(recovery_cursor=recovery_cursor)
            self._log.debug(
                f"Recovery of query SUCCEEDED "
                f"after {(recovery_cursor.get_retries())} retries."
            )
            self._after_operation(managed_operation)
        except Exception as e:
            self._log.debug(
                f"Recovery of query FAILED "
                f"after {(recovery_cursor.get_retries())} retries."
            )
            if type(e) is type(exception) and e.args == exception.args:  # re-raised
                raise exception
            raise e from exception  # keep track of originating one


def _get_query_duration(query_start_time: float):
    query_end_time = timer()
    seconds = timedelta(seconds=query_end_time - query_start_time).total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    difference = f"{int(hours):02}h:{int(minutes):02}m:{int(seconds):02}s"
    return f"duration {difference}"
