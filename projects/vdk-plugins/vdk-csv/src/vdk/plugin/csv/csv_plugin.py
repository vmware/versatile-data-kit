# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK CSV plugin script.
"""
import csv
import json
import logging
import os
import pathlib

import click
from click import Context
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.cli_run import run
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.csv.csv_ingest_job import csv_ingest_step
from vdk.plugin.sqlite import sqlite_configuration
from vdk.plugin.sqlite.ingest_to_sqlite import IngestToSQLite
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
from vdk.plugin.sqlite.sqlite_connection import SQLiteConnection

log = logging.getLogger(__name__)


@click.command(
    name="ingest-csv",
    help="Ingest CSV file."
    """
The ingestion destination depends on how vdk has been configured.
See vdk config-help  - search for "ingest" to check for possible ingestion configurations.

Examples:

\b
# This will ingest a CSV file into table with the same name as the csv file
# revenue.csv will be ingested into table revenue.
# Column names are inferred from the top row of the csv file.
vdk ingest-csv -f revenue.csv

\b
# This will ingest a CSV file into table passed as argument
vdk ingest-csv -f revenue.csv --table-name my_revenue_table

\b
# This will ingest a CSV file
# But we will switch the delimiter to tab instead of comma
# Effectively ingesting TSV (tab-separate) file.
vdk ingest-csv -f revenue.tsv --options='{"sep": "\\t"}'

\b
# This will ingest a CSV file.
# We will use custom column names.
vdk ingest-csv -f revenue.csv --options='{"names": ["gender", "os", "visits", "age", "revenue"]}'

 """,
    no_args_is_help=True,
)
@click.option(
    "-f",
    "--file",
    help="Path to the csv file. It must contain properly formatted csv file.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "-t",
    "--table-name",
    default=None,
    type=click.STRING,
    help="The table in which the csv file will be ingested into."
    "If not specified, it will default to the csv file name without the extension",
)
@click.option(
    "-o",
    "--options",
    default="{}",
    type=click.STRING,
    help="""Pass extra options when reading CSV file formatted as json. For example {"sep": ";", "verbose": true} """
    "Those are the same options as passed to pandas.read_csv. See "
    "https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html.",
)
@click.pass_context
def ingest_csv(ctx: Context, file: str, table_name: str, options: str) -> None:
    args = dict(file=file, destination_table=table_name, options=json.loads(options))
    ctx.invoke(
        run,
        data_job_directory=os.path.dirname(csv_ingest_step.__file__),
        arguments=json.dumps(args),
    )
    click.echo(f"Ingesting csv file {file} finished.")


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
    name="export-csv",
    help="Execute a SQL query against a configured database and export the result to a local CSV file.",
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.option("-n", "--name", type=click.STRING, default="result.csv", required=False)
@click.option("-p", "--path", type=click.STRING, default="", required=False)
@click.pass_context
def export_csv(ctx: click.Context, query, name: str, path: str):
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
        if not path:
            path = os.path.abspath(os.getcwd())
        fullpath = os.path.join(path, name)
        if os.path.exists(fullpath):
            click.echo(
                f"Already existing path: {fullpath}. Try again with another path or file name."
            )
        else:
            with open(fullpath, "w", encoding="UTF8", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                for row in res:
                    writer.writerow(row)
            click.echo(f"You can find the result here: {fullpath}")
            click.echo(tabulate(res, headers=column_names))
            raise Exception(f"You can find the result here: {fullpath}")


@hookimpl
def vdk_command_line(root_command: click.Group) -> None:
    root_command.add_command(ingest_csv)
    root_command.add_command(export_csv)
