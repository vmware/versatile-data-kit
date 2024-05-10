# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

import click
from tabulate import tabulate
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.postgres.ingest_to_postgres import IngestToPostgres
from vdk.plugin.postgres.postgres_connection import PostgresConnection

log = logging.getLogger(__name__)


def _connection_by_default_configuration(configuration: Configuration):
    return PostgresConnection(
        dsn=configuration.get_value("POSTGRES_DSN"),
        dbname=configuration.get_value("POSTGRES_DBNAME"),
        user=configuration.get_value("POSTGRES_USER"),
        password=configuration.get_value("POSTGRES_PASSWORD"),
        host=configuration.get_value("POSTGRES_HOST"),
        port=configuration.get_value("POSTGRES_PORT"),
    )


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for PostgreSQL with reasonable defaults
    """
    config_builder.add(
        key="POSTGRES_DSN",
        default_value=None,
        description="libpq connection string, "
        "https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING",
    )
    config_builder.add(
        key="POSTGRES_DBNAME", default_value=None, description="Database name"
    )
    config_builder.add(key="POSTGRES_USER", default_value=None, description="User name")
    config_builder.add(
        key="POSTGRES_PASSWORD", default_value=None, description="User password"
    )
    config_builder.add(
        key="POSTGRES_HOST",
        default_value=None,
        description="The host we need to connect to, defaulting to "
        "UNIX socket, https://www.psycopg.org/docs/module.html",
    )
    config_builder.add(
        key="POSTGRES_PORT",
        default_value=None,
        description="The port to connect to, defaulting to 5432",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    for section in context.core_context.configuration.list_sections():
        if section == "vdk":
            connection_name = "postgres"  # the default database
        else:
            connection_name = section.lstrip("vdk_")
            if connection_name == "vdk":
                raise ValueError(
                    "You cannot create a subsection with name 'vdk_postgres'! Try another name."
                )

        try:
            dsn = context.core_context.configuration.get_value("POSTGRES_DSN", section)
            dbname = context.core_context.configuration.get_value(
                "POSTGRES_DBNAME", section
            )
            user = context.core_context.configuration.get_value(
                "POSTGRES_USER", section
            )
            password = context.core_context.configuration.get_value(
                "POSTGRES_PASSWORD", section
            )
            host = context.core_context.configuration.get_value(
                "POSTGRES_HOST", section
            )
            port = context.core_context.configuration.get_value(
                "POSTGRES_PORT", section
            )

            if dbname and user and password and host and port:
                log.info(
                    f"Creating new Postgres connection with name {connection_name}."
                    f"The new connection is for database with name {dbname}."
                )
                context.connections.add_open_connection_factory_method(
                    connection_name.lower(),
                    lambda psql_dsn=dsn, psql_dbname=dbname, psql_user=user, psql_psswrd=password, psql_host=host, psql_port=port: PostgresConnection(
                        dsn=psql_dsn,
                        dbname=psql_dbname,
                        user=psql_user,
                        password=psql_psswrd,
                        host=psql_host,
                        port=psql_port,
                    ),
                )
                log.info(
                    f"Creating new Postgres ingester with name {connection_name}."
                    f"The new ingester is for database with name {dbname}."
                )
                context.ingester.add_ingester_factory_method(
                    connection_name.lower(),
                    lambda conn_name=connection_name.lower(), connections=context.connections: IngestToPostgres(
                        connection_name=conn_name,
                        connections=connections,
                    ),
                )
            else:
                log.warning(
                    f"New Postgres connection with name {connection_name} was not created."
                    f"Some configuration variables for {connection_name} connection are missing."
                    f"Please, check whether you have added all the mandatory values!"
                    f'You can also run vdk config-help - search for those prefixed with "POSTGRES_"'
                    f" to see what configuration options are available."
                )
        except Exception as e:
            raise Exception(
                "An error occurred while trying to create new  Postgres connections and ingesters."
                f"ERROR: {e}"
            )


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(postgres_query)


@click.command(name="postgres-query", help="executes SQL query against PostgreSQL")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def postgres_query(ctx: click.Context, query):
    click.echo(
        tabulate(
            _connection_by_default_configuration(ctx.obj.configuration).execute_query(
                query
            )
        )
    )
