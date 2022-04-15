# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import types
from abc import abstractmethod
from types import TracebackType
from typing import Any
from typing import cast
from typing import List
from typing import Optional
from typing import Type

from tenacity import before_sleep_log
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential
from vdk.api.job_input import IManagedConnection
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    ConnectionHookSpecFactory,
)
from vdk.internal.builtin_plugins.connection.managed_cursor import ManagedCursor
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.run import job_input_error_classifier
from vdk.internal.core import errors
from vdk.internal.util.decorators import closing_noexcept_on_close

logger = logging.getLogger(__name__)


class ManagedConnectionBase(PEP249Connection, IManagedConnection):
    """
    Different database providers can subclass this class to provide raw connection (by implement _connect)

    The raw connection will be managed by the application.
    Optionally further customization is allowed by plugins that implement ConnectionHookSpec
    """

    def __init__(
        self,
        log: logging.Logger = logger,
        db_con: Optional[PEP249Connection] = None,
        connection_hook_spec_factory: ConnectionHookSpecFactory = None,
    ):
        """
        this constructor MUST be called by inheritors
        """
        if log:
            self._log = log
        else:
            self._log = logging.getLogger(__name__)
        self._is_db_con_open: bool = db_con is not None
        self._db_con: Optional[PEP249Connection] = db_con
        self._connection_hook_spec_factory = connection_hook_spec_factory

    def __getattr__(self, attr):
        """
        Dynamic interception and delegation of any (non-overridden) attribute access.
        In case an attribute is not explicitly managed (customized by overriding e.g. cursor()) -
        this attribute is looked up then the call is delegated, ensuring default behaviour success path.

        First, the non-managed attribute call is redirected to the wrapped native connection if attribute available,
        otherwise to the superclass if attribute is present.
        If the attribute is not specified by both the native connection nor the superclass, an AttributeError is raised.

        For more details on customizing attributes access, see PEP562.
        """
        # native connection
        if hasattr(self._db_con, attr):
            if isinstance(getattr(self._db_con, attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(self._db_con, attr)(*args, **kwargs)

                return method
            return getattr(self._db_con, attr)
        # superclass
        if hasattr(super(), attr):
            if isinstance(getattr(super(), attr), types.MethodType):

                def method(*args, **kwargs):
                    return getattr(super(), attr)(*args, **kwargs)

                return method
            return getattr(super(), attr)
        raise AttributeError

    # Retry to connect on exception and backoff exponentially in
    # 30s, 1m, 2m, 4m
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=30, min=30, max=240),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.DEBUG),
        reraise=True,
    )
    def connect(self) -> PEP249Connection:
        """
        :return: PEP249 Connection object (managed)
        """
        if not self._is_db_con_open:
            db_con = self._connect()
            self._log.debug(f"Established {str(db_con)}")
            self._is_db_con_open = True
            self._db_con = db_con

        return self

    # def get_managed_connection(self) -> PEP249Connection:
    #     return self

    def execute_query(self, query: str) -> List[List[Any]]:
        """
        Execute SQL query.
        """
        with closing_noexcept_on_close(self._cursor()) as cur:
            cur.execute(query)

            try:
                """
                1. According to PEP 249 fetchall() should throw an exception when there is no result set
                produced by cursor.execute() (say insert into table).
                2. In pyodbc the cursor.rowcount property is always -1 => can rely upon.
                3. In impyla there is a handy property cursor.has_result_set.
                But it is not in PEP 249 and not supported by pyodbc implementation
                4. The only solution found so far is to try/catch the fetchall() call
                and swallow the exception in very narrow set of cases.
                """
                # TODO support for fetchmany
                res = cur.fetchall()
            except Exception as e:
                res = None
                if str(e) in (
                    "No results.  Previous SQL was not a query.",  # message in pyodbc
                    "Trying to fetch results on an operation with no results.",  # message in impyla
                    "no results to fetch",  # psycopg: ProgrammingError: no results to fetch
                ):
                    self._log.debug(
                        "Fetching all results from query SUCCEEDED. Query does not produce results (e.g. DROP TABLE)."
                    )
                else:
                    if job_input_error_classifier.is_user_error(e):
                        blamee = errors.ResolvableBy.USER_ERROR
                    else:
                        blamee = errors.ResolvableBy.PLATFORM_ERROR
                    errors.log_and_rethrow(
                        blamee,
                        self._log,
                        what_happened="Fetching all results from query FAILED.",
                        why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                        consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                        countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                        exception=e,
                    )
            return cast(
                List[List[Any]], res
            )  # we return None in case of DML. This is not PEP249 compliant, but is more convenient

    def cursor(self, *args, **kwargs):
        if hasattr(self._db_con, "cursor"):
            return ManagedCursor(
                self._db_con.cursor(*args, **kwargs),
                self._log,
                self._connection_hook_spec_factory,
            )
        return super().cursor()

    def commit(self, *args, **kwargs):
        if hasattr(self._db_con, "commit"):
            return self._db_con.commit(*args, **kwargs)
        return super().commit()

    def rollback(self, *args, **kwargs):
        if hasattr(self._db_con, "rollback"):
            return self._db_con.rollback(*args, **kwargs)
        return super().rollback()

    def close(self, *args, **kwargs) -> None:
        """
        Close database connection. No op if it is already closed.
        """
        try:
            if self._is_db_con_open:
                self._log.debug(f"Closing database connection {self} ... ")
                self._is_db_con_open = False
                self._db_con.close()
                self._log.debug("Closing database connection SUCCEEDED.")
        except Exception as e:
            self._log.exception(
                "Closing database connection FAILED. No problem, I'm continuing as if nothing happened.",
                e,
            )

    @abstractmethod
    def _connect(self) -> PEP249Connection:
        """
        this method MUST be implemented by inheritors and should return PEP249 Connection object (unmanaged)
        """
        raise NotImplementedError

    def _cursor(self):
        self.connect()
        return self.cursor()

    # @abstractmethod # inherit optionally e.g. in case database does not support select 1 for checks
    def _is_connected(self) -> bool:
        if None is self._is_db_con_open:
            return False
        if False is self._is_db_con_open:
            return False
        try:
            self._cursor().execute(" select 1 -- Testing if connection is alive.")
            return True
        except Exception as e:
            self._log.debug(
                f"Connection {self} is disconnected ('select 1' returned {e})"
            )
        return False

    def __enter__(self) -> Any:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:  # @UnusedVariable
        self.close()

    def __del__(self) -> None:
        self.close()

    def __str__(self) -> str:
        return "ManagedConnection[ isConnected:{} {} ]".format(
            self._is_db_con_open, self._db_con
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, PEP249Connection):
            return False
        return self._db_con == o or self._db_con == o._db_con

    def __hash__(self) -> int:
        return hash(self._db_con)
