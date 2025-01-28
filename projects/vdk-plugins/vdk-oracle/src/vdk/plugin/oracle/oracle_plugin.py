# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

import click
import oracledb
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
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
        OracleConfiguration.add_default_definition(config_builder)

    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        conf = OracleConfiguration(context.core_context.configuration)
        for section in context.core_context.configuration.list_sections():
            if section == "vdk":
                connection_name = "oracle"  # the default database
            else:
                connection_name = section.lstrip("vdk_")
                if connection_name == "oracle":
                    raise ValueError(
                        "You cannot create a subsection with name 'vdk_oracle'! Try another name."
                    )
            try:
                oracle_user, oracle_pass = conf.get_oracle_user(
                    section
                ), conf.get_oracle_password(section)
                oracle_conn_string = conf.get_oracle_connection_string(section)
                oracle_host = conf.get_oracle_host(section)
                oracle_port = conf.get_oracle_port(section)
                oracle_sid = conf.get_oracle_sid(section)

                if (
                    oracle_user
                    and oracle_pass
                    and (
                        oracle_conn_string
                        or (oracle_host and oracle_port and oracle_sid)
                    )
                ):
                    oracle_service_name = conf.get_oracle_service_name(section)
                    oracle_thick_mode = conf.oracle_thick_mode(section)
                    oracle_thick_mode_lib_dir = conf.oracle_thick_mode_lib_dir(section)
                    ingest_batch_size = conf.oracle_ingest_batch_size(section)
                    log.info(
                        f"Creating new Oracle connection with name {connection_name}."
                    )
                    context.connections.add_open_connection_factory_method(
                        connection_name.lower(),
                        lambda user=oracle_user, password=oracle_pass, conn_str=oracle_conn_string, host=oracle_host, port=oracle_port, sid=oracle_sid, service_name=oracle_service_name, thick_mode=oracle_thick_mode, thick_mode_lib_dir=oracle_thick_mode_lib_dir: OracleConnection(
                            user,
                            password,
                            conn_str,
                            host=host,
                            port=port,
                            sid=sid,
                            service_name=service_name,
                            thick_mode=thick_mode,
                            thick_mode_lib_dir=thick_mode_lib_dir,
                        ),
                    )
                    log.info(
                        f"Creating new Oracle ingester with name {connection_name}."
                    )
                    context.ingester.add_ingester_factory_method(
                        connection_name.lower(),
                        lambda conn_name=connection_name.lower(), connections=context.connections, batch_size=ingest_batch_size: IngestToOracle(
                            connection_name=conn_name,
                            connections=connections,
                            ingest_batch_size=batch_size,
                        ),
                    )
                else:
                    log.warning(
                        f"New Oracle connection with name {connection_name} was not created."
                        f"Some configuration variables for {connection_name} connection are missing."
                        f"Please, check whether you have added all the mandatory values!"
                        f'You can also run vdk config-help - search for those prefixed with "ORACLE_"'
                        f" to see what configuration options are available."
                    )
            except Exception as e:
                raise Exception(
                    "An error occurred while trying to create new  Oracle connections and ingesters."
                    f"ERROR: {e}"
                )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(OraclePlugin(), "OraclePlugin")


@click.command(
    name="oracle-query",
    help="DEPRECATED: use sql-query, instead."
    "Execute an Oracle query against an Oracle database (should be configured with env variables)",
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def oracle_query(ctx: click.Context, query):
    """
    Deprecated: "Use sql-query instead"

    oracle-query: kept for compatibility
    """
    log.warning("oracle-query has been deprecated; please use sql-query instead.")
    conf = ctx.obj.configuration
    conn = oracledb.connect(
        user=conf.get_value(key=ORACLE_USER),
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
