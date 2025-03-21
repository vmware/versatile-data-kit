# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
"""
VDK CSV plugin script.
"""
import json
import logging
import os

import click
from click import Context
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.cli_run import run
from vdk.internal.core import errors
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.csv.csv_export_job import csv_export_step
from vdk.plugin.csv.csv_ingest_job import csv_ingest_step

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
    help="Execute a SQL query against a configured database and export the result to a local CSV file."
    """
Examples:

\b
# This will execute the given query and save the data
# in a CSV file with name result.csv in the current directory
# if there is no file with the same name there
vdk export-csv -q  "SELECT * FROM test_table"

\b
# This will execute the given query and save the data
# in a CSV file with name result1.csv in User/Documents/csv
# if there is no file with the same name there
vdk export-csv -q  "SELECT * FROM test_table" -f User/Documents/csv/result1.csv

    """,
    no_args_is_help=True,
)
@click.option(
    "-q",
    "--query",
    type=click.STRING,
    required=True,
    help="The query that will be executed against the specified database.",
)
@click.option(
    "-f",
    "--file",
    help="Path to the csv file. It must not exist.",
    default=os.path.join(os.path.abspath(os.getcwd()), "result.csv"),
    type=click.Path(dir_okay=False, resolve_path=True),
)
@click.pass_context
def export_csv(ctx: click.Context, query: str, file: str):
    if os.path.exists(file):
        errors.report_and_throw(
            UserCodeError(
                "Cannot create the result csv file.",
                f"""{file} already exists. """,
                "Will not proceed with exporting",
                "Use another name or choose another location for the file",
            )
        )
    args = dict(query=query, fullpath=file)
    ctx.invoke(
        run,
        data_job_directory=os.path.dirname(csv_export_step.__file__),
        arguments=json.dumps(args),
    )


@hookimpl
def vdk_command_line(root_command: click.Group) -> None:
    root_command.add_command(ingest_csv)
    root_command.add_command(export_csv)
