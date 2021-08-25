# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
import tempfile

import click
from tabulate import tabulate
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.config import Configuration
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.sqllite_connection import SqLiteConnection

SQLITE_FILE = "SQLITE_FILE"

log = logging.getLogger(__name__)


class SqLiteConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_sqlite_file(self) -> pathlib.Path:
        return pathlib.Path(self.__config.get_value(SQLITE_FILE))


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=SQLITE_FILE,
        default_value=str(
            pathlib.Path(tempfile.gettempdir()).joinpath("vdk-sqlite.db")
        ),
        description="The file of the sqlite database.",
    )


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for sqlite with reasonable defaults
    """
    add_definitions(config_builder)


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = SqLiteConfiguration(context.core_context.configuration)
    context.connections.add_open_connection_factory_method(
        "SQLITE",
        lambda: SqLiteConnection(pathlib.Path(conf.get_sqlite_file())).new_connection(),
    )


@click.command(
    name="sqlite-query", help="executes SQL query against local SQlite database."
)
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def sqlite_query(ctx: click.Context, query):
    conf = SqLiteConfiguration(ctx.obj.configuration)
    conn = SqLiteConnection(conf.get_sqlite_file())
    res = conn.execute_query(query)
    click.echo(tabulate(res))


@hookimpl
def vdk_command_line(root_command: click.Group):
    """
    Here we extend vdk with new command called "sqlite-query" enabling users to execute
    """
    root_command.add_command(sqlite_query)
