# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Callable

import click
import pluggy
from snowflake.connector.errors import ProgrammingError
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.statestore import ImmutableStoreKey
from vdk.internal.snowflake_connection import SnowflakeConnection

"""
VDK-Snowflake Plugin
"""
log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for snowflake with reasonable defaults
    """
    config_builder.add(
        key="SNOWFLAKE_ACCOUNT",
        default_value="localhost",
        description="The Snowflake account identifier as described in https://docs.snowflake.com/en/user-guide/admin-account-identifier.html It is required to connect to a Snowflake instance.",
    )
    config_builder.add(
        key="SNOWFLAKE_SCHEMA", default_value=None, description="The database schema"
    )
    config_builder.add(
        key="SNOWFLAKE_WAREHOUSE",
        default_value=None,
        description="The warehouse to be used.",
    )
    config_builder.add(
        key="SNOWFLAKE_DATABASE",
        default_value=None,
        description="The snowflake database to be used.",
    )
    config_builder.add(
        key="SNOWFLAKE_USER", default_value="unknown", description="User name"
    )
    config_builder.add(
        key="SNOWFLAKE_PASSWORD", default_value=None, description="User password"
    )


SnowflakeConnectionFunc = Callable[[], PEP249Connection]
CONNECTION_FUNC_KEY = ImmutableStoreKey[SnowflakeConnectionFunc](
    "snowflake-connection-method"
)


@hookimpl
def vdk_initialize(context: CoreContext) -> None:
    configuration = context.configuration

    def new_connection() -> PEP249Connection:
        connection = SnowflakeConnection(
            account=configuration.get_required_value("SNOWFLAKE_ACCOUNT"),
            schema=configuration.get_value("SNOWFLAKE_SCHEMA"),
            warehouse=configuration.get_value("SNOWFLAKE_WAREHOUSE"),
            database=configuration.get_value("SNOWFLAKE_DATABASE"),
            user=configuration.get_required_value("SNOWFLAKE_USER"),
            password=configuration.get_required_value("SNOWFLAKE_PASSWORD"),
        )
        return connection

    context.state.set(CONNECTION_FUNC_KEY, new_connection)


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.connections.add_open_connection_factory_method(
        "SNOWFLAKE", context.core_context.state.get(CONNECTION_FUNC_KEY)
    )


@click.command(name="snowflake-query", help="executes SQL query against Snowflake")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def snowflake_query(ctx: click.Context, query):
    with ctx.obj.state.get(CONNECTION_FUNC_KEY)() as conn:
        res = conn.execute_query(query)
        import json

        click.echo(json.dumps(res, indent=2))


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(snowflake_query)
