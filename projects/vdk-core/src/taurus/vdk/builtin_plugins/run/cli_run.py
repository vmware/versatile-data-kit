# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import pathlib
from typing import cast
from typing import Dict
from typing import Optional

import click
from taurus.vdk.builtin_plugins.run import job_input_error_classifier
from taurus.vdk.builtin_plugins.run.data_job import DataJob
from taurus.vdk.builtin_plugins.run.data_job import DataJobDefaultHookImplPlugin
from taurus.vdk.builtin_plugins.run.data_job import DataJobFactory
from taurus.vdk.builtin_plugins.run.execution_tracking import (
    ExecutionTrackingPlugin,
)
from taurus.vdk.builtin_plugins.version import version
from taurus.vdk.core import errors
from taurus.vdk.core.context import CoreContext

log = logging.getLogger(__name__)


class CliRunImpl:
    def __init__(self, job_factory: DataJobFactory = None):
        self.__job_factory = job_factory if job_factory else DataJobFactory()

    @staticmethod
    def __validate_and_parse_args(arguments: str) -> Optional[Dict]:
        try:
            if arguments:
                return json.loads(arguments)
            else:
                return None
        except Exception as e:
            blamee = errors.ResolvableBy.USER_ERROR
            errors.log_and_rethrow(
                blamee,
                logging.getLogger(__name__),
                what_happened="Failed to validate job arguments.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION,
                exception=e,
                wrap_in_vdk_error=True,
            )

    def run_job(
        self,
        context: CoreContext,
        data_job_directory: pathlib.Path,
        arguments: Optional[str],
    ):
        log.info(f"Run job with directory {data_job_directory}")
        context.plugin_registry.load_plugin_with_hooks_impl(ExecutionTrackingPlugin())

        job = self.__job_factory.new_datajob(
            data_job_directory=data_job_directory, core_context=context
        )
        args = self.__validate_and_parse_args(arguments)

        try:
            execution_result = job.run(args)
            log.info(f"Data Job execution summary: {execution_result}")
            if execution_result.is_failed() and execution_result.get_exception():
                raise execution_result.get_exception()
        except Exception as e:
            errors.log_and_rethrow(
                job_input_error_classifier.whom_to_blame(e, __file__),
                log,
                what_happened="Failed executing job.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION
                + " Most likely a prerequisite or plugin of one of the key VDK components failed, see"
                + " logs for details and ensure the prerequisite for the failed component (details in stacktrace).",
                exception=e,
            )


@click.command(
    help="Runs a data job. "
    """
     Examples:

     \b
     # This will run the data job from directory example-job (it takes a few minutes)
     vdk run /home/user/data-jobs/example-job

"""
)
@click.argument(
    "data_job_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--arguments",
    type=click.STRING,
    required=False,
    help="Pass arguments. "
    "Those arguments will be passed to each step. "
    "Must be in valid JSON format",
)
@click.pass_context
def run(ctx: click.Context, data_job_directory: str, arguments: str) -> None:
    """
    Entry point of the CLI run. It start a run (execution) of a data job.
    """
    click.echo(
        f"Data Jobs Development Kit (VDK){os.linesep}{version.get_version_info()}",
        err=True,
    )
    click.echo("-" * 80, err=True)
    context: CoreContext = cast(CoreContext, ctx.obj)
    run_impl = CliRunImpl()
    run_impl.run_job(context, pathlib.Path(data_job_directory), arguments)
