# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib

import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.sqlite import sqlite_configuration
from vdk.plugin.sqlite.ingest_to_sqlite import IngestToSQLite
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
from vdk.plugin.sqlite.sqlite_connection import SQLiteConnection

log = logging.getLogger(__name__)


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for sqlite with reasonable defaults
    """
    sqlite_configuration.add_definitions(config_builder)


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = SQLiteConfiguration(context.core_context.configuration)
    context.connections.add_open_connection_factory_method(
        "SQLITE",
        lambda: SQLiteConnection(pathlib.Path(conf.get_sqlite_file())).new_connection(),
    )

    context.ingester.add_ingester_factory_method(
        "sqlite", (lambda: IngestToSQLite(conf))
    )


@click.command(
    name="sqlite-query", help="Execute a SQL query against a local SQLite database."
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def sqlite_query(ctx: click.Context, query):
    conf = SQLiteConfiguration(ctx.obj.configuration)
    conn = SQLiteConnection(conf.get_sqlite_file())

    with closing_noexcept_on_close(conn.new_connection().cursor()) as cursor:
        cursor.execute(query)
        column_names = (
            [column_info[0] for column_info in cursor.description]
            if cursor.description
            else ()  # same as the default value for the headers parameter of the tabulate function
        )
        res = cursor.fetchall()
        click.echo(tabulate(res, headers=column_names))


@hookimpl
def vdk_command_line(root_command: click.Group):
    """
    Here we extend vdk with new command called "sqlite-query" enabling users to execute
    """
    root_command.add_command(sqlite_query)
