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
        lineage_data = self._get_lineage_data(query, query_id)
        try:
            res = self.execute_query_with_retries(query)
            self._send_query_telemetry(query, query_id)
            self.add_num_rows_after_query(lineage_data, res)
            return res
        except Exception as e:
            self._send_query_telemetry(query, query_id, e)
            raise
        finally:
            if self._lineage_logger and lineage_data:
                self._lineage_logger.send(lineage_data)

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

    def add_num_rows_after_query(self, lineage_data, res):
        if lineage_data:
            lineage_data["output_num_rows_after"] = self._get_output_table_num_rows(
                lineage_data
            )
            if "outputTable" in lineage_data:
                if res and res[0] and res[0][0]:
                    lineage_data["output_num_rows_updated"] = res[0][0]

    def _get_lineage_data(self, query, query_id):
        if self._lineage_logger:
            try:
                with closing_noexcept_on_close(self.__cursor()) as cur:
                    cur.execute(f"EXPLAIN (TYPE IO, FORMAT JSON) {query}")
                    result = cur.fetchall()
                    if result:
                        import json

                        data = json.loads(result[0][0])
                        data["@type"] = "taurus_query_io"
                        data["query"] = query
                        data["@id"] = query_id
                        data[
                            "output_num_rows_before"
                        ] = self._get_output_table_num_rows(data)
                        return data
            except Exception as e:
                log.info(
                    f"Failed to get query io details for telemetry: {e}. Will continue with query execution"
                )
                return None

    def _get_output_table_num_rows(self, data):
        if data and "outputTable" in data:
            try:
                outputTable = data["outputTable"]
                catalog = outputTable["catalog"]
                schema = outputTable["schemaTable"]["schema"]
                table = outputTable["schemaTable"]["table"]
                # TODO: escape potential reserved names
                with closing_noexcept_on_close(self.__cursor()) as cur:
                    cur.execute(  # nosec
                        f"select count(1) from {catalog}.{schema}.{table}"
                    )
                    res = cur.fetchall()
                    if res:
                        return res[0][0]
                    else:
                        return None
            except Exception as e:
                log.info(
                    f"Failed to get output table details: {e}. Will continue with query processing as normal"
                )
                return None
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
