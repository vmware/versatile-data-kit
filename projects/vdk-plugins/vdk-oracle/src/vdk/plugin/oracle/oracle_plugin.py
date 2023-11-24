# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

import click
import oracledb
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.oracle.ingest_to_oracle import IngestToOracle
from vdk.plugin.oracle.oracle_configuration import ORACLE_CONNECTION_STRING
from vdk.plugin.oracle.oracle_configuration import ORACLE_PASSWORD
from vdk.plugin.oracle.oracle_configuration import ORACLE_USER
from vdk.plugin.oracle.oracle_configuration import OracleConfiguration
from vdk.plugin.oracle.oracle_connection import OracleConnection

"""
Include the plugins implementation. For example:
"""

log = logging.getLogger(__name__)


class OraclePlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        OracleConfiguration.add_definitions(config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext):
        conf = OracleConfiguration(context.core_context.configuration)
        context.connections.add_open_connection_factory_method(
            "ORACLE",
            lambda: OracleConnection(
                conf.get_oracle_user(),
                conf.get_oracle_password(),
                conf.get_oracle_connection_string(),
            ),
        )
        context.ingester.add_ingester_factory_method(
            "oracle", (lambda: IngestToOracle(context.connections))
        )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(OraclePlugin(), "OraclePlugin")


# TODO: https://github.com/vmware/versatile-data-kit/issues/2940
@click.command(
    name="oracle-query",
    help="Execute an Oracle query against an Oracle database (should be configured with env variables)",
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def oracle_query(ctx: click.Context, query):
    conf = ctx.obj.configuration
    conn = oracledb.connect(
        user=conf.get_value(ORACLE_USER),
        password=conf.get_value(ORACLE_PASSWORD),
        dsn=conf.get_value(ORACLE_CONNECTION_STRING),
    )

    with closing_noexcept_on_close(conn.cursor()) as cursor:
        cursor.execute(query)
        column_names = (
            [column_info[0] for column_info in cursor.description]
            if cursor.description
            else ()  # same as the default value for the headers parameters of the tabulate function
        )
        try:
            res = cursor.fetchall()
            click.echo(tabulate(res, headers=column_names))
        except Exception as e:
            if str(e) == "DPY-1003: the executed statement does not return rows":
                log.info(
                    "Query did not produce results, e.g. DROP TABLE, but was successful"
                )
            else:
                raise e
    conn.commit()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(oracle_query)
