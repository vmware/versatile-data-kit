# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import math
import os
import pathlib
import re
import sys
import traceback
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

import click
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.job_config import JobConfig
from vdk.internal.builtin_plugins.run import job_input_error_classifier
from vdk.internal.builtin_plugins.run.data_job import DataJobFactory
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.execution_tracking import (
    ExecutionTrackingPlugin,
)
from vdk.internal.builtin_plugins.version import version
from vdk.internal.core import errors
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import VdkConfigurationError

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
            log.error(
                "\n".join(
                    [
                        "Failed to validate job arguments.",
                        errors.MSG_WHY_FROM_EXCEPTION(e),
                    ]
                )
            )
            errors.report(errors.ResolvableBy.USER_ERROR, e)
            raise e

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

    @staticmethod
    def __warn_on_python_version_disparity(
        context: CoreContext, job_directory: pathlib.Path
    ):
        log_config_type = context.configuration.get_value(vdk_config.LOG_CONFIG)
        if log_config_type == "LOCAL":
            # Get the local python installation's version.
            python_env_version = sys.version_info
            local_py_version = f"{python_env_version.major}.{python_env_version.minor}"

            # Get the python_version set in the config.ini if any.
            job_path = job_directory.resolve()
            try:
                config = JobConfig(data_job_path=job_path)
            except VdkConfigurationError as e:
                log.info(
                    f"An exception occurred while loading job configuration. Error was {e}"
                )
                return
            configured_python_version = config.get_python_version()

            if not configured_python_version:
                return

            pattern = r"^\d+\.\d+"
            version_match = re.match(pattern, configured_python_version)

            if version_match:
                extracted_configured_version = version_match.group()
                if extracted_configured_version != local_py_version:
                    log.warning(
                        f"""
                        {os.linesep + (' ' * 20) + ('*' * 80)}
                        Python version mismatch between local python and configure python.
                        The Python version specified in the job's config.ini file  is ({configured_python_version})
                        while the local python version used to execute the data job is ({local_py_version}).

                        Developing a data job using one Python version and deploying
                        it with a different version can result in unexpected and
                        difficult-to-troubleshoot errors like module incompatibilities, or
                        unexpected behavior during execution.

                        To resolve this issue, ensure that the Python version
                        specified in the python_version property of the config.ini file matches
                        the Python version of your execution environment by either editing the
                        python_version property in config.ini, or switching local environment
                        to a matching version of python.
                        {os.linesep + (' ' * 20) + ('*' * 80)}
                        """
                    )

    def __log_exec_result(self, execution_result: ExecutionResult) -> None:
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

    @staticmethod
    def __log_short_exec_result(execution_result: ExecutionResult):
        def extract_relevant_lines(step: StepResult) -> List[str]:
            out = []
            if step.exception:
                call_list = traceback.format_tb(step.exception.__traceback__)

                for line_index, line in enumerate(call_list):
                    # Check if the step name is in the line
                    if step.name in line:
                        out.append(line)
                        next_line_index = line_index + 1
                        # Pull in subsequent relevant lines
                        # that do not come from another file
                        while next_line_index < len(call_list) and not re.match(
                            r'^\s*File "', call_list[next_line_index]
                        ):
                            out.append(call_list[next_line_index])
                            next_line_index += 1
                # add the exception type and message
                out.append(f"{type(step.exception).__name__}: {str(step.exception)}")
            return out

        log.info(
            "Job execution result: "
            + execution_result.status.upper()
            + "\n"
            + "Step results:\n"
            + "".join(
                [
                    step.name
                    + " - "
                    + step.status.upper()
                    + "\n"
                    + "".join(extract_relevant_lines(step))
                    for step in execution_result.steps_list
                ]
            )
        )

    def create_and_run_data_job(
        self,
        context: CoreContext,
        data_job_directory: pathlib.Path,
        arguments: Optional[str],
    ):
        log.info(f"Run job with directory {data_job_directory}")
        context.plugin_registry.load_plugin_with_hooks_impl(ExecutionTrackingPlugin())

        self.__warn_on_python_version_disparity(
            context=context, job_directory=data_job_directory
        )

        job = self.__job_factory.new_datajob(
            data_job_directory=data_job_directory, core_context=context
        )
        args = self.__validate_and_parse_args(arguments)

        execution_result = None
        try:
            execution_result = job.run(args)
            if context.configuration.get_value("LOG_EXECUTION_RESULT"):
                self.__log_exec_result(execution_result)
            else:
                self.__log_short_exec_result(execution_result)

        except BaseException as e:
            log.error(
                "\n".join(
                    [
                        "Failed executing job.",
                        errors.MSG_WHY_FROM_EXCEPTION(e),
                        " Most likely a prerequisite or plugin of one of the key VDK components failed, see"
                        + " logs for details and ensure the prerequisite for the failed component.",
                    ]
                )
            )
            errors.report(
                job_input_error_classifier.whom_to_blame(
                    e, __file__, data_job_directory
                ),
                e,
            )
            raise e
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
