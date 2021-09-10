# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import List

from snowflake.connector.errors import ProgrammingError
from tenacity import before_sleep_log
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.core import errors

log = logging.getLogger(__name__)


class SnowflakeConnection(ManagedConnectionBase):
    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        warehouse: str,
        database: str,
        schema: str,
    ):
        """
        Create a new snowflake connection. Connection parameters are:

        - *account*: snowflake account address, excluding the `.snoflakecomputing.com` part (defaults to localhost if not provided)
        - *user*: user name used to authenticate
        - *password*: password used to authenticate
        - *warehouse*: (optional) the warehouse name (only as keyword argument)
        - *database*: (optional) the database name (only as keyword argument)
        - *schema*: (optional) the schema name (only as keyword argument)
        """
        super().__init__(logging.getLogger(__name__))

        self._account = account
        self._user = user
        self._password = password
        self._warehouse = warehouse
        self._database = database
        self._schema = schema

        log.debug(
            f"Creating new snowflake connection for user: {user} for account: {account}"
        )

    def _connect(self) -> PEP249Connection:
        import snowflake.connector as sc

        log.debug(
            f"Open Snowflake Connection: account: {self._account} with user: {self._user}; "
            f"warehouse: {self._warehouse}; database: {self._database}; schema: {self._schema}"
        )

        try:
            if not self._warehouse and not self._database and not self._schema:
                return sc.connect(
                    user=self._user, password=self._password, account=self._account
                )
            else:
                return sc.connect(
                    user=self._user,
                    password=self._password,
                    account=self._account,
                    warehouse=self._warehouse,
                    database=self._database,
                    schema=self._schema,
                )
        except (errors.BaseVdkError, ProgrammingError, Exception) as e:
            blamee = errors.ResolvableBy.CONFIG_ERROR
            errors.log_and_rethrow(
                blamee,
                log,
                what_happened="Connecting to Snowflake FAILED.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                exception=e,
            )

    def execute_query(self, query) -> List[List[Any]]:
        try:
            return self.execute_query_with_retries(query)
        except errors.BaseVdkError as e:
            log.exception(f"An exception occured while executing query: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=30, min=30, max=240),
        retry=retry_if_exception_type(ProgrammingError),
        before_sleep=before_sleep_log(log, logging.DEBUG),
        reraise=True,
    )
    def execute_query_with_retries(self, query) -> List[List[Any]]:
        res = super().execute_query(query)
        return res
