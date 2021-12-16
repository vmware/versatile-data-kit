# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import ConfigurationBuilder

IMPALA_HOST = "IMPALA_HOST"
IMPALA_PORT = "IMPALA_PORT"
IMPALA_DATABASE = "IMPALA_DATABASE"
IMPALA_TIMEOUT = "IMPALA_TIMEOUT"
IMPALA_USE_SSL = "IMPALA_USE_SSL"
IMPALA_CA_CERT = "IMPALA_CA_CERT"
IMPALA_AUTH_MECHANISM = "IMPALA_AUTH_MECHANISM"
IMPALA_USER = "IMPALA_USER"
IMPALA_PW = "IMPALA_PASSWORD"
IMPALA_KERBEROS_SERVICE_NAME = "IMPALA_KERBEROS_SERVICE_NAME"
IMPALA_KRB_HOST = "IMPALA_KRB_HOST"
IMPALA_USE_HTTP_TRANSPORT = "IMPALA_USE_HTTP_TRANSPORT"
IMPALA_HTTP_PATH = "IMPALA_HTTP_PATH"
IMPALA_AUTH_COOKIE_NAMES = "IMPALA_AUTH_COOKIE_NAMES"
IMPALA_RETRIES = "IMPALA_RETRIES"
IMPALA_SYNC_DDL = "IMPALA_SYNC_DDL"
IMPALA_QUERY_POOL = "IMPALA_QUERY_POOL"


class ImpalaPluginConfiguration:
    def __init__(self, config):
        self.__config = config

    def host(self):
        return self.__config.get_value(IMPALA_HOST)

    def port(self):
        return self.__config.get_value(IMPALA_PORT)

    def database(self):
        return self.__config.get_value(IMPALA_DATABASE)

    def timeout(self):
        return self.__config.get_value(IMPALA_TIMEOUT)

    def use_ssl(self):
        return self.__config.get_value(IMPALA_USE_SSL)

    def ca_cert(self):
        return self.__config.get_value(IMPALA_CA_CERT)

    def auth_mechanism(self):
        return self.__config.get_value(IMPALA_AUTH_MECHANISM)

    def user(self):
        return self.__config.get_value(IMPALA_USER)

    def password(self):
        return self.__config.get_value(IMPALA_PW)

    def kerberos_service_name(self):
        return self.__config.get_value(IMPALA_KERBEROS_SERVICE_NAME)

    def krb_host(self):
        return self.__config.get_value(IMPALA_KRB_HOST)

    def use_http_transport(self):
        return self.__config.get_value(IMPALA_USE_HTTP_TRANSPORT)

    def http_path(self):
        return self.__config.get_value(IMPALA_HTTP_PATH)

    def auth_cookie_names(self):
        return self.__config.get_value(IMPALA_AUTH_COOKIE_NAMES)

    def retries(self):
        return self.__config.get_value(IMPALA_RETRIES)

    def sync_ddl(self):
        return self.__config.get_value(IMPALA_SYNC_DDL)

    def query_pool(self):
        return self.__config.get_value(IMPALA_QUERY_POOL)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for Impala with reasonable defaults
    """
    config_builder.add(
        key=IMPALA_HOST,
        default_value="localhost",
        description="The Impala host we want to connect to.",
    )
    config_builder.add(
        key=IMPALA_PORT,
        default_value=21050,
        description="The Impala port we want to connect to.",
    )
    config_builder.add(
        key=IMPALA_DATABASE,
        default_value=None,
        description="The Impala database that we will be running queries against.",
    )
    config_builder.add(
        key=IMPALA_TIMEOUT,
        default_value=None,
        description="Impala connection timeout in seconds.",
    )
    config_builder.add(
        key=IMPALA_USE_SSL,
        default_value=False,
        description="Enables SSL for your connection to the database.",
    )
    config_builder.add(
        key=IMPALA_CA_CERT,
        default_value=None,
        description=(
            "Local path to the the third-party CA certificate."
            "If SSL is enabled but the certificate is not specified, the server certificate will not be validated."
        ),
    )
    config_builder.add(
        key=IMPALA_AUTH_MECHANISM,
        default_value="NOSASL",
        description=(
            "The Impala authentication mechanism. `'NOSASL'` for unsecured Impala. "
            "`'PLAIN'` for unsecured Hive (because Hive requires the SASL transport). "
            "`'GSSAPI'` for Kerberos and `'LDAP'` for Kerberos with LDAP."
        ),
    )
    config_builder.add(
        key=IMPALA_USER, default_value=None, description="Your Impala username."
    )
    config_builder.add(
        key=IMPALA_PW,
        default_value=None,
        description="Your Impala password.",
    )
    config_builder.add(
        key=IMPALA_KERBEROS_SERVICE_NAME,
        default_value=None,
        description="Used to authenticate to a particular `impalad` service principal. Uses `'impala'` by default.",
    )
    config_builder.add(
        key=IMPALA_KRB_HOST, default_value=None, description="The Kerberos host."
    )
    config_builder.add(
        key=IMPALA_USE_HTTP_TRANSPORT,
        default_value=False,
        description="Enables http transport; default is binary transport.",
    )
    config_builder.add(
        key=IMPALA_HTTP_PATH,
        default_value="",
        description="The path in the http URL. Used only when `impala_use_http_transport` is True.",
    )
    config_builder.add(
        key=IMPALA_AUTH_COOKIE_NAMES,
        default_value=None,
        description=(
            "The list of possible names for the cookie used for cookie-based authentication. "
            "If the list of names contains one cookie name only, a str value can be specified instead of a list. "
            "Used only when `impala_use_http_transport` is True. By default 'impala_auth_cookie_names' is set to the "
            "list of auth cookie names used by Impala and Hive. If 'impala_auth_cookie_names' is explicitly set to "
            "an empty value (None, [], or ''), VDK won't attempt to do cookie based authentication. "
            "Currently cookie-based authentication is only supported for GSSAPI over http."
        ),
    )
    config_builder.add(
        key=IMPALA_RETRIES,
        default_value=3,
        description="The number of retries VDK will attempt when connecting to or running a query against Impala.",
    )
    config_builder.add(
        key=IMPALA_SYNC_DDL,
        default_value=False,
        description=(
            "If enabled, DDL operations will return only when the changes have been propagated to all other "
            "Impala nodes in the cluster. For more information, see "
            "https://impala.apache.org/docs/build/html/topics/impala_sync_ddl.html"
        ),
    )
    config_builder.add(
        key=IMPALA_QUERY_POOL,
        default_value=None,
        description="The name of the Impala pool to execute queries in.",
    )
