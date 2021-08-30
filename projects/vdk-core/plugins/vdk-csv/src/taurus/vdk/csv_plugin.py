# Copyright (c) 2021 VMware, Inc.
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
See vdk config-help  - search for "ingest" to check for possible ingestion conifgurations.

Examples:

\b
# This will ingest a CSV file into table with the same name as the csv file
# revenue.csv will be ingested into table revenue.
vdkcli ingest-csv revenue.csv

\b
# This will ingest a CSV file into table passed as argument
vdkcli ingest-csv revenue.csv --table-name my_revenue_table

\b
# This will ingest a CSV file into table passed as argument
# But we can switch the delimiter to tab instead of command
# Effectively ingesting TSV file.
vdkcli ingest-csv revenue.tsv --options="{'sep': '\\t'}"

               """,
    no_args_is_help=True,
)
@click.option(
    "-f",
    "--file",
    help="Path to the csv file. It must contain at least properly formatted csv file.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "-t",
    "--table-name",
    default=None,
    type=click.STRING,
    help="Path to the csv file. It must contain properly formatted csv file. "
    "It will default to the csv file name without the extension",
)
@click.option(
    "-o",
    "--options",
    default="{}",
    type=click.STRING,
    help="Pass extra options when reading CSV file formatted as json. For example {'sep': ';', 'verbose': true} "
    "Those are the same options as passed to pandas.read_csv"
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


@hookimpl
def vdk_command_line(root_command: click.Group) -> None:
    root_command.add_command(ingest_csv)
