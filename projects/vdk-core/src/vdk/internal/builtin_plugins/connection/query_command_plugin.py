# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from pathlib import Path

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.util.decorators import closing_noexcept_on_close

OUTPUT_OPTIONS = ["json", "text"]

# The command is hidden as it's still experimental.
# TODOs:
# Remove logs  by default only show output (and perhaps warning logs)
# When logging omit "job details" logs
# Make clear how it is authenticated.


@click.command(
    name="sql-query",
    hidden=True,  # Hidden as it is experimental
    help="executes SQL query against configured database. "
    "The database used is configured with 'db_default_type' option. "
    "See vdk config-help for more info. ",
)
@click.option(
    "-q", "--query", type=click.STRING, required=True, help="The query to be executed"
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(OUTPUT_OPTIONS, False),
    default="text",
    help=f"Output format. It can be one of: {OUTPUT_OPTIONS}.",
)
@click.pass_context
def sql_query(ctx: click.Context, query: str, output: str) -> None:
    # TODO: os.getcwd() is passed to StandaloneDataJob, this means that if the current directory is same as data job
    # it would authenticate using the data job credentials (if there are any like keytab)
    # Is that a good idea?

    from vdk.internal.builtin_plugins.run.standalone_data_job import (
        StandaloneDataJobFactory,
    )

    with StandaloneDataJobFactory.create(
        data_job_directory=Path(os.getcwd())
    ) as job_input:
        conn: ManagedConnectionBase = job_input.get_managed_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            column_names = (
                [column_info[0] for column_info in cursor.description]
                if cursor.description
                else ()  # same as the default value for the headers parameter of the tabulate function
            )
            # TODO: this is basically emulating
            # https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-control-cli/src/vdk/internal/control/utils/output_printer.py
            # It will be best printer functionality to be reusable (either moved to vdk-core or in a library/plugin)
            result = cursor.fetchall()
            if output.lower() == "json":
                result = [
                    {column_names[i]: v for i, v in enumerate(row)} for row in result
                ]
                click.echo(json.dumps(result))
            elif output.lower() == "text":
                from tabulate import tabulate

                click.echo(tabulate(result, headers=column_names))
            else:
                raise ValueError(
                    f"Unsupported output format. Choose between: {OUTPUT_OPTIONS}"
                )


class QueryCommandPlugin:
    @staticmethod
    @hookimpl
    def vdk_command_line(root_command: click.Group) -> None:
        root_command.add_command(sql_query)
