# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.greenplum.greenplum_connection import GreenplumConnection
from vdk.plugin.greenplum.ingest_to_greenplum import IngestToGreenplum


def _connection_by_configuration(configuration: Configuration):
    return GreenplumConnection(
        dsn=configuration.get_value("GREENPLUM_DSN"),
        dbname=configuration.get_value("GREENPLUM_DBNAME"),
        user=configuration.get_value("GREENPLUM_USER"),
        password=configuration.get_value("GREENPLUM_PASSWORD"),
        host=configuration.get_value("GREENPLUM_HOST"),
        port=configuration.get_value("GREENPLUM_PORT"),
    )


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for Greenplum with reasonable defaults
    """
    config_builder.add(
        key="GREENPLUM_DSN",
        default_value=None,
        description="libpq connection string, "
        "https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING",
    )
    config_builder.add(
        key="GREENPLUM_DBNAME", default_value=None, description="Database name"
    )
    config_builder.add(
        key="GREENPLUM_USER", default_value=None, description="User name"
    )
    config_builder.add(
        key="GREENPLUM_PASSWORD", default_value=None, description="User password"
    )
    config_builder.add(
        key="GREENPLUM_HOST",
        default_value=None,
        description="The host we need to connect to, defaulting to "
        "UNIX socket, https://www.psycopg.org/docs/module.html",
    )
    config_builder.add(
        key="GREENPLUM_PORT",
        default_value=None,
        description="The port to connect to, defaulting to 5432",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.connections.add_open_connection_factory_method(
        "GREENPLUM",
        lambda: _connection_by_configuration(context.core_context.configuration),
    )
    context.ingester.add_ingester_factory_method(
        "GREENPLUM", lambda: IngestToGreenplum(context)
    )


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(greenplum_query)


@click.command(name="greenplum-query", help="executes SQL query against Greenplum")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def greenplum_query(ctx: click.Context, query):
    click.echo(
        tabulate(
            _connection_by_configuration(ctx.obj.configuration).execute_query(query)
        )
    )
