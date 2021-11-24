# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from impala.dbapi import connect as impala_connect
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)

_log = logging.getLogger(__name__)


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
        super().__init__(_log)

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
            timeout=self._timeout,
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

    def execute_query(self, query: str):
        return super().execute_query(query)
