# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

import click
import duckdb
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.duckdb import duckdb_configuration
from vdk.plugin.duckdb.duckdb_configuration import DUCKDB_CONFIGURATION_DICTIONARY
from vdk.plugin.duckdb.duckdb_configuration import DUCKDB_DATABASE
from vdk.plugin.duckdb.duckdb_configuration import DuckDBConfiguration
from vdk.plugin.duckdb.ingest_to_duckdb import IngestToDuckDB

log = logging.getLogger(__name__)
"""
Include the plugins implementation. For example:
"""


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """Define the configuration settings needed for duckdb"""
    duckdb_configuration.add_definitions(config_builder)


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = DuckDBConfiguration(context.core_context.configuration)

    context.connections.add_open_connection_factory_method(
        "DUCKDB", lambda: duckdb.connect(conf.get_duckdb_database())
    )

    context.ingester.add_ingester_factory_method(
        "duckdb",
        (
            lambda: IngestToDuckDB(
                conf, lambda: context.connections.open_connection("DUCKDB")
            )
        ),
    )


@click.command(
    name="duckdb-query", help="Execute a DuckDB query against a local DUCKDB database."
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def duckdb_query(ctx: click.Context, query):
    conf = ctx.obj.configuration
    duckdb_db = conf.get_value(DUCKDB_DATABASE)
    conn = duckdb.connect(database=duckdb_db)

    with closing_noexcept_on_close(conn.cursor()) as cursor:
        cursor.execute(query)
        column_names = (
            [column_info[0] for column_info in cursor.description]
            if cursor.description
            else ()  # same as the default value for the headers parameters of the tabulate function
        )
        res = cursor.fetchall()
        click.echo(tabulate(res, headers=column_names))


@hookimpl
def vdk_command_line(root_command: click.Group):
    """Here we extend the vdk with a new command called "duckdb-query"
    enabling users to execute"""
    root_command.add_command(duckdb_query)
