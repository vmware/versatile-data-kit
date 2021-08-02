# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from abc import abstractmethod
from types import TracebackType
from typing import Any
from typing import cast
from typing import List
from typing import Optional
from typing import Type

from taurus.api.job_input import IManagedConnection
from taurus.vdk.builtin_plugins.connection.managed_cursor import ManagedCursor
from taurus.vdk.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from taurus.vdk.core import errors
from taurus.vdk.util.decorators import closing_noexcept_on_close
from tenacity import before_sleep_log
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential

logger = logging.getLogger(__name__)


class ManagedConnectionBase(PEP249Connection, IManagedConnection):
    """
    Different database providers can subclass this class to provide raw connection (by implement _connect)

    The raw connection will be managed by the application.
    Optionally further customization is allowed by overriding _cursor_execute and_before_cursor_execute
    """

    def __init__(
        self, log: logging.Logger = logger, db_con: Optional[PEP249Connection] = None
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

    @abstractmethod
    def _connect(self) -> PEP249Connection:
        """
        this method MUST be implemented by inheritors and should return PEP249 Connection object (unmanaged)
        """
        raise NotImplementedError

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
        :return: PEP249 Connection object (unmanaged)
        """
        if not self._is_db_con_open:
            db_con = self._connect()
            self._log.debug("Established %s", str(db_con))
            self._is_db_con_open = True
            self._db_con = db_con
        return self._db_con

    # @abstractmethod # inherit optionally
    def _before_cursor_execute(self, cur: ManagedCursor) -> None:
        pass

    # @abstractmethod # inherit optionally
    def _cursor_execute(self, cur: ManagedCursor, query: str) -> None:
        cur.execute(query)  # no need to log around this method.

    def execute_query(self, query: str) -> List[List[Any]]:
        """
        Execute SQL query.
        """
        # TODO: configurable generic re-try.
        try:
            #  query = query.encode('utf-8') #TODO make it a validation step and fail if query is not UTF-8
            #  query = query.decode('utf-8') #TODO make it a validation step and fail if query is not UTF-8
            with closing_noexcept_on_close(self.__cursor()) as cur:
                self._before_cursor_execute(cur)
                self._cursor_execute(cur, query)

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
                except Exception as pe:
                    res = None
                    # TODO: this will likely not work in other dbs.
                    if str(pe) in (
                        "No results.  Previous SQL was not a query.",  # message in pyodbc
                        "Trying to fetch results on an operation with no results.",  # message in impyla
                        "no results to fetch",  # psycopg: ProgrammingError: no results to fetch
                    ):
                        self._log.debug(
                            "Fetching all results from query SUCCEEDED. Query does not produce results (e.g. DROP "
                            "TABLE). "
                        )
                    else:
                        self._log.debug("Fetching all results from query FAILED.")
                        raise
                    # we return None in case of DML. This is not PEP249 compliant, but is more convenient
                return cast(List[List[Any]], res)
        except Exception as e:
            # without knowing anything most likely issue in SQL query is due to job owner.
            # Plugins may override this.
            blamee = errors.ResolvableBy.USER_ERROR
            errors.log_and_rethrow(
                blamee,
                self._log,
                what_happened="Executing query FAILED.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                exception=e,
            )
            return []

    def __cursor(self) -> ManagedCursor:
        conn = self.connect()
        cur = conn.cursor()
        return ManagedCursor(cur, self._log)

    # @abstractmethod # inherit optionally e.g. in case database does not support select 1 for checks
    def _is_connected(self) -> bool:
        if None is self._is_db_con_open:
            return False
        if False is self._is_db_con_open:
            return False
        try:
            self.__cursor().execute(" select 1 -- Testing if connection is alive.")
            return True
        except Exception as e:
            self._log.debug(
                f"Connection {self} is disconnected ('select 1' returned {e})"
            )
        return False

    def get_managed_connection(self) -> PEP249Connection:
        return self

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

    def close(self) -> None:
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

    def __str__(self) -> str:
        return "ManagedConnection[ isConnected:{} {} ]".format(
            self._is_db_con_open, self._db_con
        )
