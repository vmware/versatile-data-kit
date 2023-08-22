# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib

import click
import duckdb
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)
"""
Include the plugins implementation. For example:
"""


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """Define the configuration settings needed for duckdb"""
    config_builder.add("DUCKDB_FILE", default_value="mydb.duckdb")


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = context.core_context.configuration
    duckdb_file = conf.get_value("DUCKDB_FILE")

    context.connections.add_open_connection_factory_method(
        "DUCKDB", lambda: duckdb.connect(database=duckdb_file)
    )


@click.command(
    name="duckdb-query", help="Execute a DuckDB query against a local DUCKDB database."
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def duckdb_query(ctx: click.Context, query):
    conf = ctx.obj.configuration
    duckdb_file = conf.get_value("DUCKDB_FILE")
    conn = duckdb.connect(database=duckdb_file)

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
