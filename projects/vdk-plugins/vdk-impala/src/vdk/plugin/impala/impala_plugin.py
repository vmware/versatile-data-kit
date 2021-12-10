# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.impala.impala_configuration import add_definitions
from vdk.plugin.impala.impala_configuration import ImpalaPluginConfiguration
from vdk.plugin.impala.impala_connection import ImpalaConnection
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler


def _connection_by_configuration(configuration: ImpalaPluginConfiguration):
    return ImpalaConnection(
        host=configuration.host(),
        port=configuration.port(),
        database=configuration.database(),
        timeout=configuration.timeout(),
        use_ssl=configuration.use_ssl(),
        ca_cert=configuration.ca_cert(),
        auth_mechanism=configuration.auth_mechanism(),
        user=configuration.user(),
        password=configuration.password(),
        kerberos_service_name=configuration.kerberos_service_name(),
        krb_host=configuration.krb_host(),
        use_http_transport=configuration.use_http_transport(),
        http_path=configuration.http_path(),
        auth_cookie_names=configuration.auth_cookie_names(),
        retries=configuration.retries(),
    )


@click.command(name="impala-query", help="executes SQL query against Impala")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def impala_query(ctx: click.Context, query):
    impala_cfg = ImpalaPluginConfiguration(ctx.obj.configuration)
    click.echo(tabulate(_connection_by_configuration(impala_cfg).execute_query(query)))


class ImpalaPlugin:
    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @staticmethod
    @hookimpl
    def vdk_command_line(root_command: click.Group):
        root_command.add_command(impala_query)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._impala_cfg = ImpalaPluginConfiguration(
            context.core_context.configuration
        )  # necessary for the query decoration hook
        context.connections.add_open_connection_factory_method(
            "IMPALA",
            lambda: _connection_by_configuration(self._impala_cfg),
        )

    @staticmethod
    @hookimpl
    def db_connection_recover_operation(recovery_cursor: RecoveryCursor) -> None:
        impala_error_handler = ImpalaErrorHandler()

        if impala_error_handler.handle_error(
            recovery_cursor.get_exception(), recovery_cursor
        ):
            logging.getLogger(__name__).info(
                "Error handled successfully! Query execution has succeeded."
            )
        else:
            raise recovery_cursor.get_exception()

    @hookimpl(tryfirst=True)
    def db_connection_decorate_operation(self, decoration_cursor: DecorationCursor):
        if self._impala_cfg.sync_ddl():
            decoration_cursor.execute("SET SYNC_DDL=True")
        if self._impala_cfg.query_pool():
            decoration_cursor.execute(
                f"SET REQUEST_POOL='{self._impala_cfg.query_pool()}'"
            )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(ImpalaPlugin())
