# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import types
from typing import Any
from typing import cast
from typing import Collection
from typing import Container
from typing import Optional

from vdk.api.plugin.connection_hook_spec import (
    ConnectionHookSpec,
)
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core import errors


class ManagedCursor(PEP249Cursor):
    """
    PEP249 Cursor
    """

    def __init__(
        self,
        cursor: Any,
        log: logging.Logger = None,
        connection_hook_spec: ConnectionHookSpec = None,
    ):
        if not log:
            log = logging.getLogger(__name__)
        super().__init__(cursor, log)
        self.__connection_hook_spec = connection_hook_spec

    def __getattr__(self, attr):
        """
        Dynamic interception and delegation of any (non-overridden) attribute access.
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
        if self.__connection_hook_spec:
            if (
                self.__connection_hook_spec.db_connection_validate_operation.get_hookimpls()
            ):
                self._log.debug("Validating query:\n%s" % operation)
                try:
                    self.__connection_hook_spec.db_connection_validate_operation(
                        operation=operation, parameters=parameters
                    )
                except Exception as e:
                    errors.log_and_rethrow(
                        errors.ResolvableBy.USER_ERROR,
                        self._log,
                        what_happened="Validating query FAILED.",
                        why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                        consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                        countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                        exception=e,
                    )

            if (
                self.__connection_hook_spec.db_connection_decorate_operation.get_hookimpls()
            ):
                self._log.debug("Decorating query:\n%s" % operation)
                decoration_cursor = DecorationCursor(
                    self._cursor, self._log, managed_operation
                )

                try:
                    self.__connection_hook_spec.db_connection_decorate_operation(
                        decoration_cursor=decoration_cursor
                    )
                except Exception as e:
                    errors.log_and_rethrow(
                        errors.ResolvableBy.PLATFORM_ERROR,
                        self._log,
                        what_happened="Decorating query FAILED.",
                        why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                        consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                        countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                        exception=e,
                    )

        self._log.info("Executing query:\n%s" % managed_operation.get_operation())
        try:
            super().execute(*managed_operation.get_operation_parameters_tuple())
            self._log.info("Executing query SUCCEEDED.")
        except Exception as e:
            try:
                self._recover_operation(e, managed_operation)
            except Exception as e:
                # todo: error classification
                # if job_input_error_classifier.is_user_error(e):
                blamee = errors.ResolvableBy.USER_ERROR
                # else:
                #     blamee = errors.ResolvableBy.PLATFORM_ERROR
                errors.log_and_rethrow(
                    blamee,
                    self._log,
                    what_happened="Executing query FAILED.",
                    why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                    consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                    countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                    exception=e,
                )

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
        if (
            not self.__connection_hook_spec
            or not self.__connection_hook_spec.db_connection_recover_operation.get_hookimpls()
        ):
            raise exception

        recovery_cursor = RecoveryCursor(
            self._cursor,
            self._log,
            exception,
            managed_operation,
            self.__connection_hook_spec.db_connection_decorate_operation,
        )
        self._log.debug(f"Recovery of query {managed_operation.get_operation()}")
        try:
            self.__connection_hook_spec.db_connection_recover_operation(
                recovery_cursor=recovery_cursor
            )
            self._log.debug(
                f"Recovery of query SUCCEEDED "
                f"after {(recovery_cursor.get_retries())} retries."
            )
        except Exception as e:
            self._log.debug(
                f"Recovery of query FAILED "
                f"after {(recovery_cursor.get_retries())} retries."
            )
            if type(e) is type(exception) and e.args == exception.args:  # re-raised
                raise exception
            raise e from exception  # keep track of originating one
