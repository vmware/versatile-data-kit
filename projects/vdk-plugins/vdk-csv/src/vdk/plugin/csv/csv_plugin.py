# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK CSV plugin script.
"""
import csv
import json
import logging
import os

import click
from click import Context
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.cli_run import run
from vdk.internal.core import errors
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.csv.csv_ingest_job import csv_ingest_step
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


@click.command(
    name="export-csv",
    help="Execute a SQL query against a configured database and export the result to a local CSV file.",
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.option("-n", "--name", type=click.STRING, default="result.csv", required=False)
@click.option("-p", "--path", type=click.STRING, default="", required=False)
@click.pass_context
def export_csv(ctx: click.Context, query, name: str, path: str):
    if not path:
        path = os.path.abspath(os.getcwd())
    fullpath = os.path.join(path, name)
    if os.path.exists(fullpath):
        errors.log_and_throw(
            errors.ResolvableBy.USER_ERROR,
            log,
            "Cannot create the result csv file.",
            f"""File with name {name} already exists in {path} """,
            "Will not proceed with exporting",
            "Use another name or choose another location for the file",
        )
    conf = SQLiteConfiguration(ctx.obj.configuration)
    conn = SQLiteConnection(conf.get_sqlite_file())
    with closing_noexcept_on_close(conn.new_connection().cursor()) as cursor:
        cursor.execute(query)
        res = cursor.fetchall()
        if not res:
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                "Cannot create the result csv file.",
                f"""No data was found """,
                "Will not proceed with exporting",
                "Try with another query or check the database explicitly.",
            )

        with open(fullpath, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            for row in res:
                writer.writerow(row)
        click.echo(f"You can find the result here: {fullpath}")


@hookimpl
def vdk_command_line(root_command: click.Group) -> None:
    root_command.add_command(ingest_csv)
    root_command.add_command(export_csv)
