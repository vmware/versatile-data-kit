# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import base64
import json
import logging
from typing import Optional

import requests
from tenacity import before_sleep_log
from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_exponential
from trino import constants
from trino import dbapi
from trino.auth import BasicAuthentication
from trino.exceptions import TrinoExternalError
from trino.exceptions import TrinoInternalError
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.trino.trino_config import TrinoConfiguration
from vdk.plugin.trino.trino_error_handler import TrinoErrorHandler

log = logging.getLogger(__name__)


class TrinoConnection(ManagedConnectionBase):
    def __init__(
        self,
        configuration: TrinoConfiguration,
        section: Optional[str],
        lineage_logger=None,
    ):
        """
        Create a new database connection. Connection parameters are:

        - *host*: database host address (defaults to localhost if not provided)
        - *port*: connection port number (defaults to 8080 if not provided)
        - *catalog*: the catalog name (only as keyword argument)
        - *schema*: the schema name (only as keyword argument)
        - *user*: username used to authenticate
        """
        super().__init__(logging.getLogger(__name__))

        self._host = configuration.host(section)
        self._port = configuration.port(section)
        self._catalog = configuration.catalog(section)
        self._schema = configuration.schema(section)
        self._user = configuration.user(section)
        self._password = configuration.password(section)
        self._use_ssl = configuration.use_ssl(section)
        self._ssl_verify = configuration.ssl_verify(section)
        self._timeout_seconds = configuration.timeout_seconds(section)
        self._retries_on_error = configuration.retries(section)
        self._error_backoff_seconds = configuration.backoff_interval_seconds(section)

        self._lineage_logger = lineage_logger

        self._use_team_oauth = configuration.use_team_oauth(section)

        if self._use_team_oauth:
            self._team_client_id = configuration.team_client_id()
            self._team_client_secret = configuration.team_client_secret()
            self._team_oauth_url = configuration.team_oauth_url()
            log.debug(
                f"Creating new trino connection for oAuth ClientID: {self._team_client_id} to host: {self._host}:{self._port}"
            )
        else:
            log.debug(
                f"Creating new trino connection for user: {self._user} to host: {self._host}:{self._port}"
            )

    def _connect(self):
        if self._use_team_oauth:
            return self._team_oauth_connection()
        else:
            return self._basic_authentication_connection()

    def _team_oauth_connection(self):
        log.debug(
            f"Open Trino Connection: host: {self._host}:{self._port} with oAuth ClientID: {self._team_client_id}; "
            f"catalog: {self._catalog}; schema: {self._schema}; timeout: {self._timeout_seconds}"
        )

        oauth_token = self._get_access_token()

        # Create an OAuth session
        session = OAuthSession(oauth_token)

        connection = dbapi.connect(
            host=self._host,
            port=self._port,
            catalog=self._catalog,
            schema=self._schema,
            http_scheme=constants.HTTPS if self._use_ssl else constants.HTTP,
            verify=self._ssl_verify,
            request_timeout=self._timeout_seconds,
            http_session=session,
        )
        return connection

    def _get_access_token(self):
        # Exchange client ID & Secret for an access token
        # Original basic auth string
        original_string = self._team_client_id + ":" + self._team_client_secret
        # Encode
        encoded_bytes = base64.b64encode(original_string.encode("utf-8"))
        encoded_string = encoded_bytes.decode("utf-8")

        headers = {
            "Authorization": "Basic " + encoded_string,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(self._team_oauth_url, headers=headers, data=data)
        # If this call fails then, we better raise it as early as possible
        response.raise_for_status()

        response_json = json.loads(response.text)
        oauth_token = response_json["access_token"]
        return oauth_token

    def _basic_authentication_connection(self):
        log.debug(
            f"Open Trino Connection: host: {self._host}:{self._port} with user: {self._user}; "
            f"catalog: {self._catalog}; schema: {self._schema}; timeout: {self._timeout_seconds}"
        )
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

    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        trino_error_handler = TrinoErrorHandler(
            num_retries=self._retries_on_error,
            backoff_seconds=self._error_backoff_seconds,
        )
        if trino_error_handler.handle_error(
            recovery_cursor.get_exception(), recovery_cursor
        ):
            logging.getLogger(__name__).debug(
                "Error handled successfully! Query execution has succeeded."
            )
        else:
            raise recovery_cursor.get_exception()

    def execute_query(self, query):
        res = self.execute_query_with_retries(query)
        if self._lineage_logger:
            lineage_data = self._get_lineage_data(query)
            if lineage_data:
                self._lineage_logger.send(lineage_data)
        #  TODO: collect lineage for failed query
        return res

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

    def _get_lineage_data(self, query):
        from vdk.plugin.trino import lineage_utils
        import sqlparse

        statement = sqlparse.parse(query)[0]

        if statement.get_type() == "ALTER":
            rename_table_lineage = lineage_utils.get_rename_table_lineage_from_query(
                query, self._schema, self._catalog
            )
            if rename_table_lineage:
                log.debug("Collecting lineage for rename table operation ...")
                return rename_table_lineage
            else:
                log.debug(
                    "ALTER operation not a RENAME TABLE operation. No lineage will be collected."
                )

        elif statement.get_type() == "SELECT" or statement.get_type() == "INSERT":
            if lineage_utils.is_heartbeat_query(query):
                return None
            log.debug("Collecting lineage for SELECT/INSERT query ...")
            try:
                with closing_noexcept_on_close(self._cursor()) as cur:
                    cur.execute(f"EXPLAIN (TYPE IO, FORMAT JSON) {query}")
                    result = cur.fetchall()
                    if result:
                        return lineage_utils.get_lineage_data_from_io_explain(
                            query, result[0][0]
                        )
            except Exception as e:
                log.info(
                    f"Failed to get query io details for telemetry: {e}. Will continue with query execution"
                )
                return None
        else:
            log.debug(
                "Unsupported query type for lineage collection. Will not collect lineage."
            )
            return None

        return None


# Define a custom requests session to add the OAuth token to the headers
class OAuthSession(requests.Session):
    def __init__(self, token):
        super().__init__()
        self.headers.update({"Authorization": f"Bearer {token}"})
