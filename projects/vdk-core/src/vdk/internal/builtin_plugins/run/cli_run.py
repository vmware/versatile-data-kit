# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import math
import os
import pathlib
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

import click
from vdk.internal.builtin_plugins.run import job_input_error_classifier
from vdk.internal.builtin_plugins.run.data_job import DataJobFactory
from vdk.internal.builtin_plugins.run.execution_tracking import (
    ExecutionTrackingPlugin,
)
from vdk.internal.builtin_plugins.version import version
from vdk.internal.core import errors
from vdk.internal.core.context import CoreContext

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

    @staticmethod
    def __split_into_chunks(exec_steps: List, chunks: int) -> List:
        """
        Generator that splits the list of execution steps into sequential
        sub-lists.
        :param exec_steps: the list of execution steps
        :param chunks: the number of sublists that need to be produced
        :return: a list of the sub-lists produced
        """
        quotient, remainder = divmod(len(exec_steps), chunks)
        for i in range(chunks):
            subsequent_iteration = (quotient + 1) * (
                i if i < remainder else remainder
            ) + quotient * (0 if i < remainder else i - remainder)
            yield exec_steps[
                subsequent_iteration : subsequent_iteration
                + (quotient + 1 if i < remainder else quotient)
            ]

    def create_and_run_data_job(
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

        execution_result = None
        try:
            execution_result = job.run(args)

            # On some platforms, if the size of a string is too large, the
            # logging module starts throwing OSError: [Errno 40] Message too long,
            # so it is safer if we split large strings into smaller chunks.
            string_exec_result = str(execution_result)
            if len(string_exec_result) > 5000:
                temp_exec_result = json.loads(string_exec_result)
                steps = temp_exec_result.pop("steps_list")

                log.info(
                    f"Data Job execution summary: {json.dumps(temp_exec_result, indent=2)}"
                )

                chunks = math.ceil(len(string_exec_result) / 5000)
                for i in self.__split_into_chunks(exec_steps=steps, chunks=chunks):
                    log.info(f"Execution Steps: {json.dumps(i, indent=2)}")

            else:
                log.info(f"Data Job execution summary: {execution_result}")
        except BaseException as e:
            errors.log_and_rethrow(
                job_input_error_classifier.whom_to_blame(
                    e, __file__, data_job_directory
                ),
                log,
                what_happened="Failed executing job.",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION
                + " Most likely a prerequisite or plugin of one of the key VDK components failed, see"
                + " logs for details and ensure the prerequisite for the failed component (details in stacktrace).",
                exception=e,
            )
        if execution_result.is_failed() and execution_result.get_exception_to_raise():
            raise execution_result.get_exception_to_raise()


@click.command(
    help="Run a Data Job. "
    """
     Examples:

     \b
     # This will run the Data Job from directory example-job (it takes a few minutes)
     vdk run /home/user/data-jobs/example-job
     \b
     # Run data job with arguments.
     vdk run example-job --arguments '{"key1": "value1","key2": "value2"}'

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
    "Must be in valid JSON format. "
    "Arguments are passed to each step. "
    "They can be used as parameters in SQL queries and will be replaced automatically."
    "Properties can also be specified as parameters in SQL, arguments would have higher priority for the same key.",
)
@click.pass_context
def run(ctx: click.Context, data_job_directory: str, arguments: str) -> None:
    """
    Entry point of the CLI run. It start a run (execution) of a data job.
    """
    log.info(
        f"Versatile Data Kit (VDK){os.linesep}{version.get_version_info()}{os.linesep + '-' * 80}"
    )
    context: CoreContext = cast(CoreContext, ctx.obj)
    run_impl = CliRunImpl()
    run_impl.create_and_run_data_job(
        context, pathlib.Path(data_job_directory), arguments
    )
