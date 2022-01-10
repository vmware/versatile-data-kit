# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import Callable
from typing import Optional

import click
import pluggy
import requests
from tabulate import tabulate
from trino.exceptions import TrinoUserError
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import ImmutableStoreKey
from vdk.internal.core.statestore import StoreKey
from vdk.plugin.trino import trino_config
from vdk.plugin.trino.ingest_to_trino import IngestToTrino
from vdk.plugin.trino.lineage import LineageLogger
from vdk.plugin.trino.trino_config import TrinoConfiguration
from vdk.plugin.trino.trino_connection import TrinoConnection

log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    trino_config.add_definitions(config_builder)


LINEAGE_LOGGER_KEY = StoreKey[LineageLogger]("trino-lineage-logger")

TrinoConnectionFunc = Callable[[], PEP249Connection]
CONNECTION_FUNC_KEY = ImmutableStoreKey[TrinoConnectionFunc]("trino-connection-method")


@hookimpl
def vdk_initialize(context: CoreContext) -> None:
    configuration = TrinoConfiguration(context.configuration)

    def new_connection() -> PEP249Connection:
        connection = TrinoConnection(
            host=configuration.host(),
            port=configuration.port(),
            schema=configuration.schema(),
            catalog=configuration.catalog(),
            user=configuration.user(),
            password=configuration.password(),
            use_ssl=configuration.use_ssl(),
            ssl_verify=configuration.ssl_verify(),
            timeout_seconds=configuration.timeout_seconds(),
            lineage_logger=context.state.get(LINEAGE_LOGGER_KEY),
        )
        return connection

    context.state.set(CONNECTION_FUNC_KEY, new_connection)

    trino_config.trino_templates_data_to_target_strategy = (
        configuration.templates_data_to_target_strategy()
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

    context.ingester.add_ingester_factory_method(
        "trino", (lambda: IngestToTrino(context))
    )


@hookimpl(hookwrapper=True, tryfirst=True)
def run_step(context: JobContext, step: Step) -> None:
    out: pluggy.callers._Result
    out = yield
    if out.excinfo:
        exc_type, exc_value, exc_traceback = out.excinfo
        if isinstance(exc_value, TrinoUserError):
            raise UserCodeError(ErrorMessage()) from exc_value
    if out.result:
        step_result: StepResult = out.result
        if isinstance(step_result.exception, requests.exceptions.ConnectionError):
            raise VdkConfigurationError(
                ErrorMessage(
                    summary="Trino query failed",
                    what="Trino query failed with connectivity error",
                    why=f"Error message was: {step_result.exception}. "
                    f"Likely the query has a configuration error that needs to be address."
                    f" See above error message for more details.",
                    consequences="The SQL query will fail and the job step likely will fail.",
                    countermeasures="Please fix the error and try again. "
                    "Verify the current trino configuration with vdk config-help.",
                ),
            ) from step_result.exception
        if isinstance(step_result.exception, TrinoUserError):
            raise UserCodeError(
                ErrorMessage(
                    summary="Trino query failed",
                    what="Trino query failed with user error",
                    why=f"Error message was: {step_result.exception.message}. "
                    f"Likely the query has an syntax error that needs to be addressed."
                    f" See above error message for more details.",
                    consequences="The SQL query will fail and the job step likely will fail.",
                    countermeasures="Please fix the error and try again.",
                )
            ) from step_result.exception


@click.command(name="trino-query", help="Execute a SQL query against a Trino database.")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def trino_query(ctx: click.Context, query):
    with ctx.obj.state.get(CONNECTION_FUNC_KEY)() as conn:
        res = conn.execute_query(query)
        click.echo(tabulate(res))


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
