# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib

import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.job_config import JobConfig
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.decorators import closing_noexcept_on_close
from vdk.plugin.sqlite import sqlite_configuration
from vdk.plugin.sqlite.ingest_to_sqlite import IngestToSQLite
from vdk.plugin.sqlite.sqlite_configuration import SQLITE_FILE
from vdk.plugin.sqlite.sqlite_configuration import SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
from vdk.plugin.sqlite.sqlite_connection import SQLiteConnection

log = logging.getLogger(__name__)


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for sqlite with reasonable defaults
    """
    sqlite_configuration.add_default_definitions(config_builder)


@hookimpl
def initialize_job(context: JobContext) -> None:
    conf = SQLiteConfiguration(context.core_context.configuration)
    multiple_dbs = conf.get_sqlite_multiple_db()
    multiple_dbs = multiple_dbs.split(",")
    if len(multiple_dbs) == 0:
        context.connections.add_open_connection_factory_method(
            "SQLITE",
            lambda: SQLiteConnection(
                pathlib.Path(conf.get_sqlite_file())
            ).new_connection(),
        )

        context.ingester.add_ingester_factory_method(
            "sqlite", (lambda: IngestToSQLite(conf))
        )
    else:
        all_conf = JobConfig(context.job_directory).get_vdk_options()

        def _get_config_or_env(key, default=None):
            """Attempt to get the configuration from environment variables first, falling back to all_conf."""
            return os.getenv("VDK_" + key, default=all_conf.get(key.lower(), default))

        for db in multiple_dbs:
            curr_db_file_key = db + "_" + SQLITE_FILE
            curr_db_ingest_auto_key = db + "_" + SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED

            new_builder = ConfigurationBuilder()
            # here we need to add descriptions for all the conf
            new_builder.add(
                key=SQLITE_FILE,
                default_value=pathlib.Path(_get_config_or_env(curr_db_file_key)),
            )
            new_builder.add(
                key=SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED,
                default_value=_get_config_or_env(curr_db_ingest_auto_key),
            )

            # we need to handle secrets as well for example in oracle -> user and password

            new_config = SQLiteConfiguration(new_builder.build())

            context.connections.add_open_connection_factory_method(
                db.upper(),
                lambda: SQLiteConnection(
                    pathlib.Path(new_config.get_sqlite_file())
                ).new_connection(),
            )

            context.ingester.add_ingester_factory_method(
                db.lower(), (lambda: IngestToSQLite(new_config))
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
