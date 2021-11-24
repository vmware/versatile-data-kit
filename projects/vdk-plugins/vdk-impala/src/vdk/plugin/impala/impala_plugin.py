# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.impala.impala_connection import ImpalaConnection


def _connection_by_configuration(configuration: Configuration):
    return ImpalaConnection(
        host=configuration.get_value("IMPALA_HOST"),
        port=configuration.get_value("IMPALA_PORT"),
        database=configuration.get_value("IMPALA_DATABASE"),
        timeout=configuration.get_value("IMPALA_TIMEOUT"),
        use_ssl=configuration.get_value("IMPALA_USE_SSL"),
        ca_cert=configuration.get_value("IMPALA_CA_CERT"),
        auth_mechanism=configuration.get_value("IMPALA_AUTH_MECHANISM"),
        user=configuration.get_value("IMPALA_USER"),
        password=configuration.get_value("IMPALA_PASSWORD"),
        kerberos_service_name=configuration.get_value("IMPALA_KERBEROS_SERVICE_NAME"),
        krb_host=configuration.get_value("IMPALA_KRB_HOST"),
        use_http_transport=configuration.get_value("IMPALA_USE_HTTP_TRANSPORT"),
        http_path=configuration.get_value("IMPALA_HTTP_PATH"),
        auth_cookie_names=configuration.get_value("IMPALA_AUTH_COOKIE_NAMES"),
        retries=configuration.get_value("IMPALA_RETRIES"),
    )


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for Impala with reasonable defaults
    """
    config_builder.add(
        key="IMPALA_HOST",
        default_value="localhost",
        description="The Impala host we want to connect to.",
    )
    config_builder.add(
        key="IMPALA_PORT",
        default_value=21050,
        description="The Impala port we want to connect to.",
    )
    config_builder.add(
        key="IMPALA_DATABASE",
        default_value=None,
        description="The Impala database that we will be running queries against.",
    )
    config_builder.add(
        key="IMPALA_TIMEOUT",
        default_value=None,
        description="Impala connection timeout in seconds.",
    )
    config_builder.add(
        key="IMPALA_USE_SSL",
        default_value=False,
        description="Enables SSL for your connection to the database.",
    )
    config_builder.add(
        key="IMPALA_CA_CERT",
        default_value=None,
        description=(
            "Local path to the the third-party CA certificate."
            "If SSL is enabled but the certificate is not specified, the server certificate will not be validated."
        ),
    )
    config_builder.add(
        key="IMPALA_AUTH_MECHANISM",
        default_value="NOSASL",
        description=(
            "The Impala authentication mechanism. `'NOSASL'` for unsecured Impala. "
            "`'PLAIN'` for unsecured Hive (because Hive requires the SASL transport). "
            "`'GSSAPI'` for Kerberos and `'LDAP'` for Kerberos with LDAP."
        ),
    )
    config_builder.add(
        key="IMPALA_USER", default_value=None, description="Your Impala username."
    )
    config_builder.add(
        key="IMPALA_PASSWORD", default_value=None, description="Your Impala password."
    )
    config_builder.add(
        key="IMPALA_KERBEROS_SERVICE_NAME",
        default_value=None,
        description="Used to authenticate to a particular `impalad` service principal. Uses `'impala'` by default.",
    )
    config_builder.add(
        key="IMPALA_KRB_HOST", default_value=None, description="The Kerberos host."
    )
    config_builder.add(
        key="IMPALA_USE_HTTP_TRANSPORT",
        default_value=False,
        description="Enables http transport; default is binary transport.",
    )
    config_builder.add(
        key="IMPALA_HTTP_PATH",
        default_value="",
        description="The path in the http URL. Used only when `impala_use_http_transport` is True.",
    )
    config_builder.add(
        key="IMPALA_AUTH_COOKIE_NAMES",
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
        key="IMPALA_RETRIES",
        default_value=3,
        description="The number of retries VDK will attempt when connecting to or running a query against Impala.",
    )


@click.command(name="impala-query", help="executes SQL query against Impala")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def impala_query(ctx: click.Context, query):
    click.echo(
        tabulate(
            _connection_by_configuration(ctx.obj.configuration).execute_query(query)
        )
    )


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(impala_query)


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.connections.add_open_connection_factory_method(
        "IMPALA",
        lambda: _connection_by_configuration(context.core_context.configuration),
    )
