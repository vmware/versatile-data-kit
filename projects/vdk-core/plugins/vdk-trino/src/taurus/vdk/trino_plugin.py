# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import Callable
from typing import Optional

import click
import pluggy
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk import trino_config
from taurus.vdk.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.builtin_plugins.run.step import Step
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.errors import UserCodeError
from taurus.vdk.core.statestore import ImmutableStoreKey
from taurus.vdk.core.statestore import StoreKey
from taurus.vdk.lineage import LineageLogger
from taurus.vdk.trino_connection import TrinoConnection
from trino.exceptions import TrinoUserError

log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for trino with reasonable defaults
    """
    config_builder.add(
        key="TRINO_HOST",
        default_value="localhost",
        description="The host we need to connect.",
    )
    config_builder.add(
        key="TRINO_PORT", default_value=28080, description="The port to connect to"
    )
    config_builder.add(
        key="TRINO_USE_SSL",
        default_value=True,
        description="Set if database connection uses SSL",
    )
    config_builder.add(
        key="TRINO_SSL_VERIFY",
        default_value=True,
        description="Verify the SSL certificate",
    )
    config_builder.add(
        key="TRINO_SCHEMA", default_value="default", description="The database schema"
    )
    config_builder.add(
        key="TRINO_CATALOG", default_value="memory", description="The database catalog"
    )
    config_builder.add(
        key="TRINO_USER", default_value="unknown", description="User name"
    )
    config_builder.add(
        key="TRINO_PASSWORD", default_value=None, description="User password"
    )
    config_builder.add(
        key="TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY",
        default_value="INSERT_SELECT",
        description="What strategy is used when moving data from source table to target table in templates."
        "Possible values are:\n"
        "INSERT_SELECT - target is created, data from source is inserted into target, source is dropped;\n"
        "RENAME - source is renamed to target;\n",
    )


LINEAGE_LOGGER_KEY = StoreKey[LineageLogger]("trino-lineage-logger")

TrinoConnectionFunc = Callable[[], PEP249Connection]
CONNECTION_FUNC_KEY = ImmutableStoreKey[TrinoConnectionFunc]("trino-connection-method")


@hookimpl
def vdk_initialize(context: CoreContext) -> None:
    configuration = context.configuration

    def new_connection() -> PEP249Connection:
        connection = TrinoConnection(
            host=configuration.get_required_value("TRINO_HOST"),
            port=configuration.get_required_value("TRINO_PORT"),
            schema=configuration.get_value("TRINO_SCHEMA"),
            catalog=configuration.get_value("TRINO_CATALOG"),
            user=configuration.get_required_value("TRINO_USER"),
            password=configuration.get_value("TRINO_PASSWORD"),
            use_ssl=configuration.get_value("TRINO_USE_SSL"),
            ssl_verify=configuration.get_value("TRINO_SSL_VERIFY"),
            timeout_seconds=configuration.get_value("DB_CONNECTIONS_TIMEOUT_SECONDS"),
            lineage_logger=context.state.get(LINEAGE_LOGGER_KEY),
        )
        return connection

    context.state.set(CONNECTION_FUNC_KEY, new_connection)

    trino_config.trino_templates_data_to_target_strategy = configuration.get_value(
        "TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY"
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.connections.add_open_connection_factory_method(
        "TRINO", context.core_context.state.get(CONNECTION_FUNC_KEY)
    )

    context.templates.add_template(
        "scd1", pathlib.Path(get_job_path("load/dimension/scd1"))
    )

    context.templates.add_template(
        "scd2", pathlib.Path(get_job_path("load/dimension/scd2"))
    )

    context.templates.add_template(
        "periodic_snapshot", pathlib.Path(get_job_path("load/fact/periodic_snapshot"))
    )


@hookimpl(hookwrapper=True, trylast=True)
def run_step(context: JobContext, step: Step) -> None:
    out: pluggy.callers._Result
    out = yield
    if out.excinfo:
        exc_type, exc_value, exc_traceback = out.excinfo
        if isinstance(exc_value, TrinoUserError):
            raise UserCodeError() from exc_value


@click.command(name="trino-query", help="executes SQL query against Trino")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def trino_query(ctx: click.Context, query):
    with ctx.obj.state.get(CONNECTION_FUNC_KEY)() as conn:
        res = conn.execute_query(query)
        import json

        print(json.dumps(res, indent=2))


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(trino_query)


def get_jobs_parent_directory() -> pathlib.Path:
    current_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    jobs_dir = current_dir.joinpath("templates")
    return jobs_dir


def get_job_path(job_name: str) -> str:
    """Get the path of the test data job returned as string so it can be passed easier as cmd line args"""
    return str(get_jobs_parent_directory().joinpath(job_name))
