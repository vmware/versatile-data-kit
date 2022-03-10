# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import time

from tenacity import before_sleep_log
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential
from trino.exceptions import TrinoExternalError
from trino.exceptions import TrinoInternalError
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)


class TrinoConnection(ManagedConnectionBase):
    def __init__(
        self,
        host,
        port,
        catalog,
        schema,
        user,
        password,
        use_ssl=True,
        ssl_verify=True,
        timeout_seconds=120,
        lineage_logger=None,
    ):
        """
        Create a new database connection. Connection parameters are:

        - *host*: database host address (defaults to localhost if not provided)
        - *port*: connection port number (defaults to 8080 if not provided)
        - *catalog*: the catalog name (only as keyword argument)
        - *schema*: the schema name (only as keyword argument)
        - *user*: user name used to authenticate
        """
        super().__init__(logging.getLogger(__name__))

        self._host = host
        self._port = port
        self._catalog = catalog
        self._schema = schema
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._ssl_verify = ssl_verify
        self._timeout_seconds = timeout_seconds
        self._lineage_logger = lineage_logger
        log.debug(
            f"Creating new trino connection for user: {user} to host: {host}:{port}"
        )

    def _connect(self):
        from trino import dbapi
        from trino import constants

        log.debug(
            f"Open Trino Connection: host: {self._host}:{self._port} with user: {self._user}; "
            f"catalog: {self._catalog}; schema: {self._schema}; timeout: {self._timeout_seconds}"
        )
        from trino.auth import BasicAuthentication

        auth = (
            BasicAuthentication(self._user, self._password) if self._password else None
        )
        conn = dbapi.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            auth=auth,
            catalog=self._catalog,
            schema=self._schema,
            http_scheme=constants.HTTPS if self._use_ssl else constants.HTTP,
            verify=self._ssl_verify,
            request_timeout=self._timeout_seconds,
        )
        return conn

    def execute_query(self, query):
        query_id = str(time.time())
        try:
            res = self.execute_query_with_retries(query)
            if self._lineage_logger:
                lineage_data = self._get_lineage_data(query, query_id)
                if lineage_data:
                    self._lineage_logger.send(lineage_data)
            return res
        except Exception as e:
            self._send_query_telemetry(query, query_id, e)
            raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=30, min=30, max=240),
        retry=retry_if_exception_type((TrinoExternalError, TrinoInternalError)),
        before_sleep=before_sleep_log(log, logging.DEBUG),
        reraise=True,
    )
    def execute_query_with_retries(self, query):
        res = super().execute_query(query)
        return res

    def _get_lineage_data(self, query, query_id):

        from vdk.plugin.trino import lineage_utils
        import sqlparse

        statement = sqlparse.parse(query)[0]

        if statement.get_type() == "ALTER":
            rename_table_names = lineage_utils.parse_rename_table_names(query)
            if rename_table_names:
                return {
                    "@id": query_id,
                    "@type": "rename_table",
                    "table_from": rename_table_names[0],
                    "table_to": rename_table_names[1],
                    "query": query,
                    "status": "OK",
                }

        elif statement.get_type() == "SELECT" or statement.get_type() == "INSERT":
            try:
                with closing_noexcept_on_close(self._cursor()) as cur:
                    cur.execute(f"EXPLAIN (TYPE IO, FORMAT JSON) {query}")
                    result = cur.fetchall()
                    if result:
                        import json

                        data = json.loads(result[0][0])
                        data["@type"] = lineage_utils.determine_query_type_from_plan(
                            data
                        )
                        data["query"] = query
                        data["@id"] = query_id
                        data["status"] = "OK"
                        return data
            except Exception as e:
                log.info(
                    f"Failed to get query io details for telemetry: {e}. Will continue with query execution"
                )
                return None
        else:
            return None

    def _send_query_telemetry(self, query, query_id, exception=None):
        if self._lineage_logger:
            try:
                data = dict()
                data["@type"] = "taurus_query"
                data["query"] = query
                data["@id"] = query_id
                data["status"] = "OK" if exception is None else "EXCEPTION"
                if exception:
                    data["error_message"] = str(exception)
                self._lineage_logger.send(data)
            except:
                log.exception("Failed to send query details as telemetry.")
