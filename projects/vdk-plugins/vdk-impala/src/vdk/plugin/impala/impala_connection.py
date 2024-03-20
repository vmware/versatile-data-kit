# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from impala.dbapi import connect as impala_connect
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler

log = logging.getLogger(__name__)


class ImpalaConnection(ManagedConnectionBase):
    def __init__(
        self,
        host="localhost",
        port=21050,
        database=None,
        timeout=None,
        use_ssl=False,
        ca_cert=None,
        auth_mechanism="NOSASL",
        user=None,
        password=None,
        kerberos_service_name="impala",
        krb_host=None,
        use_http_transport=False,
        http_path="",
        auth_cookie_names=None,
        retries=3,
    ):
        super().__init__(log)

        self._host = host
        self._port = port
        self._database = database
        self._timeout = timeout
        self._use_ssl = use_ssl
        self._ca_cert = ca_cert
        self._auth_mechanism = auth_mechanism
        self._user = user
        self._password = password
        self._kerberos_service_name = kerberos_service_name
        self._krb_host = krb_host
        self._use_http_transport = use_http_transport
        self._http_path = http_path
        self._auth_cookie_names = auth_cookie_names
        self._retries = retries

    def _connect(self):
        conn = impala_connect(
            host=self._host,
            port=self._port,
            database=self._database,
            timeout=int(self._timeout) if self._timeout else None,
            use_ssl=self._use_ssl,
            ca_cert=self._ca_cert,
            auth_mechanism=self._auth_mechanism,
            user=self._user,
            password=self._password,
            kerberos_service_name=self._kerberos_service_name,
            krb_host=self._krb_host,
            use_http_transport=self._use_http_transport,
            http_path=self._http_path,
            auth_cookie_names=self._auth_cookie_names,
            retries=self._retries,
        )

        return conn

    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        impala_error_handler = ImpalaErrorHandler(
            num_retries=self._impala_cfg.retries_on_error(),
            backoff_seconds=self._impala_cfg.error_backoff_seconds(),
        )

        if impala_error_handler.handle_error(
            recovery_cursor.get_exception(), recovery_cursor
        ):
            logging.getLogger(__name__).debug(
                "Error handled successfully! Query execution has succeeded."
            )
        else:
            raise recovery_cursor.get_exception()

    def db_connection_decorate_operation(self, decoration_cursor: DecorationCursor):
        if self._impala_cfg.sync_ddl():
            try:
                decoration_cursor.execute("SET SYNC_DDL=True")
            except Exception as e:
                logging.getLogger(__name__).error(
                    "Failed to execute 'SET SYNC_DDL=True'"
                )
                if self._db_default_type.lower() == "impala":
                    raise e
        if self._impala_cfg.query_pool():
            try:
                decoration_cursor.execute(
                    f"SET REQUEST_POOL='{self._impala_cfg.query_pool()}'"
                )
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to execute 'SET REQUEST_POOL='{self._impala_cfg.query_pool()}'"
                )
                if self._db_default_type.lower() == "impala":
                    raise e
