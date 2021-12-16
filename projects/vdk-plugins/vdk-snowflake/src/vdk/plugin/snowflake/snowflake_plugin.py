# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.snowflake.snowflake_configuration import add_definitions
from vdk.plugin.snowflake.snowflake_configuration import SnowflakeConfiguration
from vdk.plugin.snowflake.snowflake_connection import SnowflakeConnection

"""
VDK-Snowflake Plugin
"""
log = logging.getLogger(__name__)


def _new_snowflake_connection(configuration: Configuration) -> PEP249Connection:
    """
    Create new Snowflake connection instance.
    """
    config = SnowflakeConfiguration(configuration)
    return SnowflakeConnection(
        account=config.get_snowflake_account(),
        user=config.get_snowflake_user(),
        password=config.get_snowflake_password(),
        warehouse=config.get_snowflake_warehouse(),
        database=config.get_snowflake_database(),
        schema=config.get_snowflake_schema(),
    )


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for snowflake with reasonable defaults
    """
    add_definitions(config_builder)


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.connections.add_open_connection_factory_method(
        "SNOWFLAKE",
        lambda: _new_snowflake_connection(context.core_context.configuration),
    )


@click.command(name="snowflake-query", help="executes SQL query against Snowflake")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def snowflake_query(ctx: click.Context, query):
    from tabulate import tabulate

    conn = _new_snowflake_connection(ctx.obj.configuration)

    click.echo(tabulate(conn.execute_query(query)))
    conn.close()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(snowflake_query)
