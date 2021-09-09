# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK CSV plugin script.
"""
import json
import logging
import os

import click
from click import Context
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.cli_run import run
from taurus.vdk.csv_ingest_job import csv_ingest_step

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
vdkcli ingest-csv -f revenue.csv

\b
# This will ingest a CSV file into table passed as argument
vdkcli ingest-csv -f revenue.csv --table-name my_revenue_table

\b
# This will ingest a CSV file
# But we will switch the delimiter to tab instead of comma
# Effectively ingesting TSV (tab-separate) file.
vdkcli ingest-csv -f revenue.tsv --options='{"sep": "\\t"}'

\b
# This will ingest a CSV file.
# We will use custom column names.
vdkcli ingest-csv -f revenue.csv --options='{"names": ["gender", "os", "visits", "age", "revenue"]}'

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
def vdk_command_line(root_command: click.Group) -> None:
    root_command.add_command(ingest_csv)
