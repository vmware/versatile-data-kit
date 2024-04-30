# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import List

import click
import requests
from tabulate import tabulate
from trino.exceptions import TrinoUserError
from vdk.api.lineage.model.logger.lineage_logger import ILineageLogger
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import StoreKey
from vdk.plugin.trino import trino_config
from vdk.plugin.trino.ingest_to_trino import IngestToTrino
from vdk.plugin.trino.trino_config import TRINO_CATALOG
from vdk.plugin.trino.trino_config import TRINO_HOST
from vdk.plugin.trino.trino_config import TRINO_PASSWORD
from vdk.plugin.trino.trino_config import TRINO_PORT
from vdk.plugin.trino.trino_config import TRINO_SCHEMA
from vdk.plugin.trino.trino_config import TRINO_SSL_VERIFY
from vdk.plugin.trino.trino_config import TRINO_TIMEOUT_SECONDS
from vdk.plugin.trino.trino_config import TRINO_USE_SSL
from vdk.plugin.trino.trino_config import TRINO_USER
from vdk.plugin.trino.trino_config import TrinoConfiguration
from vdk.plugin.trino.trino_connection import TrinoConnection

log = logging.getLogger(__name__)

LINEAGE_LOGGER_KEY = StoreKey[ILineageLogger]("trino-lineage-logger")


class TrinoPlugin:
    def __init__(self, lineage_logger: ILineageLogger = None):
        self._lineage_logger = lineage_logger

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        TrinoConfiguration.add_definitions(config_builder)

    @hookimpl(trylast=True)
    def vdk_initialize(self, context: CoreContext) -> None:
        configuration = TrinoConfiguration(context.configuration)
        trino_config.trino_templates_data_to_target_strategy = (
            configuration.templates_data_to_target_strategy(None)
        )

    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        trino_conf = TrinoConfiguration(context.core_context.configuration)

        context.templates.add_template(
            "scd1", pathlib.Path(get_job_path("load/dimension/scd1"))
        )

        context.templates.add_template(
            "scd2", pathlib.Path(get_job_path("load/dimension/scd2"))
        )

        context.templates.add_template(
            "periodic_snapshot",
            pathlib.Path(get_job_path("load/fact/periodic_snapshot")),
        )

        for section in context.core_context.configuration.list_sections():
            if section == "vdk":
                connection_name = "trino"  # the default database
            else:
                connection_name = section.lstrip("vdk_")

            host = trino_conf.host(section)
            port = trino_conf.port(section)

            if host and port:
                schema = trino_conf.schema(section)
                catalog = trino_conf.catalog(section)
                user = trino_conf.user(section)
                password = trino_conf.password(section)
                use_ssl = trino_conf.use_ssl(section)
                ssl_verify = trino_conf.ssl_verify(section)
                timeout_seconds = trino_conf.timeout_seconds(section)
                lineage_logger = context.core_context.state.get(LINEAGE_LOGGER_KEY)

                context.connections.add_open_connection_factory_method(
                    connection_name.lower(),
                    lambda t_host=host, t_port=port, t_schema=schema, t_catalog=catalog, t_user=user, t_password=password, t_use_ssl=use_ssl, t_ssl_verify=ssl_verify, t_timeout=timeout_seconds, t_lineage_logger=lineage_logger: TrinoConnection(
                        host=t_host,
                        port=t_port,
                        schema=t_schema,
                        catalog=t_catalog,
                        user=t_user,
                        password=t_password,
                        use_ssl=t_use_ssl,
                        ssl_verify=t_ssl_verify,
                        timeout_seconds=t_timeout,
                        lineage_logger=t_lineage_logger,
                    ),
                )

                context.ingester.add_ingester_factory_method(
                    connection_name.lower(),
                    lambda connections=context.connections, name=connection_name.lower(): IngestToTrino(
                        connection_name=name, connections=connections
                    ),
                )

        @hookimpl(hookwrapper=True, tryfirst=True)
        def run_step(context: JobContext, step: Step) -> None:
            out: HookCallResult
            out = yield
            if out.excinfo:
                exc_type, exc_value, exc_traceback = out.excinfo
                if isinstance(exc_value, TrinoUserError):
                    raise UserCodeError() from exc_value
            if out.get_result():
                step_result: StepResult = out.get_result()
                if isinstance(
                    step_result.exception, requests.exceptions.ConnectionError
                ):
                    raise VdkConfigurationError(
                        "Trino query failed",
                        "Trino query failed with connectivity error",
                        f"Error message was: {step_result.exception}. "
                        "Likely the query has a configuration error that needs to be address."
                        " See above error message for more details.",
                        "The SQL query will fail and the job step likely will fail.",
                        "Please fix the error and try again. "
                        "Verify the current trino configuration with vdk config-help.",
                    ) from step_result.exception
                if isinstance(step_result.exception, TrinoUserError):
                    raise UserCodeError(
                        "Trino query failed",
                        "Trino query failed with user error",
                        f"Error message was: {step_result.exception.message}. "
                        "Likely the query has an syntax error that needs to be addressed."
                        " See above error message for more details.",
                        "The SQL query will fail and the job step likely will fail.",
                        "Please fix the error and try again.",
                    ) from step_result.exception


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(TrinoPlugin(), "TrinoPlugin")


@click.command(name="trino-query", help="Execute a SQL query against a Trino database.")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def trino_query(ctx: click.Context, query):
    conf = ctx.obj.configuration
    conn = TrinoConnection(
        host=conf.get_value(TRINO_HOST),
        port=conf.get_value(TRINO_PORT),
        schema=conf.get_value(TRINO_SCHEMA),
        catalog=conf.get_value(TRINO_CATALOG),
        user=conf.get_value(TRINO_USER),
        password=conf.get_value(TRINO_PASSWORD),
        use_ssl=conf.get_value(TRINO_USE_SSL),
        ssl_verify=conf.get_value(TRINO_SSL_VERIFY),
        timeout_seconds=conf.get_value(TRINO_TIMEOUT_SECONDS),
        lineage_logger=ctx.obj.state.get(LINEAGE_LOGGER_KEY),
    )

    with conn as connection:
        res = connection.execute_query(query)
        click.echo(tabulate(res))
        connection.close()


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
