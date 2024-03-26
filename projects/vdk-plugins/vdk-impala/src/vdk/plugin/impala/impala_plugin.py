# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import List

import click
from tabulate import tabulate
from vdk.api.lineage.model.logger.lineage_logger import ILineageLogger
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.impala.impala_configuration import add_definitions
from vdk.plugin.impala.impala_configuration import ImpalaPluginConfiguration
from vdk.plugin.impala.impala_connection import ImpalaConnection
from vdk.plugin.impala.impala_error_classifier import is_impala_user_error
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.impala.impala_lineage import LINEAGE_LOGGER_KEY


def _connection_by_configuration(
    configuration: ImpalaPluginConfiguration, lineage_logger: ILineageLogger = None
):
    return ImpalaConnection(
        host=configuration.host(),
        port=configuration.port(),
        database=configuration.database(),
        timeout=configuration.timeout(),
        use_ssl=configuration.use_ssl(),
        ca_cert=configuration.ca_cert(),
        auth_mechanism=configuration.auth_mechanism(),
        user=configuration.user(),
        password=configuration.password(),
        kerberos_service_name=configuration.kerberos_service_name(),
        krb_host=configuration.krb_host(),
        use_http_transport=configuration.use_http_transport(),
        http_path=configuration.http_path(),
        auth_cookie_names=configuration.auth_cookie_names(),
        retries=configuration.retries(),
        retries_on_error=configuration.retries_on_error(),
        error_backoff_seconds=configuration.error_backoff_seconds(),
        sync_ddl=configuration.sync_ddl,
        query_pool=configuration.query_pool,
        db_default_type="impala",
        lineage_logger=lineage_logger,
    )


@click.command(name="impala-query", help="executes SQL query against Impala")
@click.option("-q", "--query", type=click.STRING, required=True)
@click.pass_context
def impala_query(ctx: click.Context, query):
    impala_cfg = ImpalaPluginConfiguration(ctx.obj.configuration)
    click.echo(tabulate(_connection_by_configuration(impala_cfg).execute_query(query)))


class ImpalaPlugin:
    def __init__(self, lineage_logger: ILineageLogger = None):
        self._lineage_logger = lineage_logger

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)

    @staticmethod
    @hookimpl
    def vdk_command_line(root_command: click.Group):
        root_command.add_command(impala_query)

    # the purpose of the below hook is to get reference to any registered lineage loggers by other plugins
    @hookimpl(
        trylast=True
    )  # trylast because we want to have any lineage loggers already initialized
    def vdk_initialize(self, context: CoreContext) -> None:
        self._lineage_logger = context.state.get(LINEAGE_LOGGER_KEY)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._db_default_type = context.core_context.configuration.get_value(
            "DB_DEFAULT_TYPE"
        )

        self._impala_cfg = ImpalaPluginConfiguration(context.core_context.configuration)
        context.connections.add_open_connection_factory_method(
            "IMPALA",
            lambda: _connection_by_configuration(
                self._impala_cfg, self._lineage_logger
            ),
        )

        context.templates.add_template(
            "load/dimension/scd1", pathlib.Path(get_job_path("load/dimension/scd1"))
        )

        context.templates.add_template(
            "scd1", pathlib.Path(get_job_path("load/dimension/scd1"))
        )

        context.templates.add_template(
            "load/dimension/scd2", pathlib.Path(get_job_path("load/dimension/scd2"))
        )

        context.templates.add_template(
            "scd2_simple", pathlib.Path(get_job_path("load/dimension/scd2"))
        )

        context.templates.add_template(
            "load/fact/snapshot", pathlib.Path(get_job_path("load/fact/snapshot"))
        )

        context.templates.add_template(
            "periodic_snapshot", pathlib.Path(get_job_path("load/fact/snapshot"))
        )

        context.templates.add_template(
            "insert", pathlib.Path(get_job_path("load/fact/insert"))
        )

        context.templates.add_template(
            "load/versioned", pathlib.Path(get_job_path("load/versioned"))
        )
        context.templates.add_template(
            "scd2", pathlib.Path(get_job_path("load/versioned"))
        )

    @staticmethod
    @hookimpl(hookwrapper=True, tryfirst=True)
    def run_step(context: JobContext, step: Step) -> None:
        out: HookCallResult
        out = yield

        exception = out.get_result().exception
        if exception:
            exception = (
                exception.__cause__
                if hasattr(exception, "__cause__") and exception.__cause__
                else exception
            )
            if is_impala_user_error(exception):
                raise UserCodeError(
                    ErrorMessage(
                        summary="Error occurred.",
                        what=f"Error occurred. Exception message: {exception}",
                        why="Review exception for details.",
                        consequences="Data Job execution will not continue.",
                        countermeasures="Review exception for details.",
                    )
                ) from exception


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(ImpalaPlugin(), "impala-plugin")


def get_jobs_parent_directory() -> pathlib.Path:
    current_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    jobs_dir = current_dir.joinpath("templates")
    return jobs_dir


def get_job_path(job_name: str) -> str:
    """Get the path of the test data job returned as string so it can be passed easier as cmd line args"""
    return str(get_jobs_parent_directory().joinpath(job_name))
