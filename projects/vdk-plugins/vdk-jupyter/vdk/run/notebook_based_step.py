# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import inspect
import logging
import pathlib
import sys
import types
from typing import Callable
from typing import List

from notebook_step import NotebookStep
from vdk.api.job_input import IJobInput
from vdk.internal.core import errors
from vdk.internal.core.errors import SkipRemainingStepsException

log = logging.getLogger(__name__)


class JobNotebookLocator:
    """
    Locate the data job files that would be executed by us.
    """

    def get_notebook_files(self, directory: pathlib.Path) -> List[pathlib.Path]:
        """Locates the files in a directory, that are supported for execution.
        Files supported for execution are: .ipynb
        Other files in the directory are ignored.
        :return: List of files from the directory that supported for execution, sorted alphabetically by name.
        :rtype: :class:`.list`
        """
        script_files = [
            x for x in directory.iterdir() if (x.name.lower().endswith(".ipynb"))
        ]
        script_files.sort(key=lambda x: x.name)
        log.debug(f"Script files of {directory} are {script_files}")
        return script_files


class NotebookStepFuncFactory:
    """
    Implementations of runner_func for running Notebook steps
    """

    @staticmethod
    def run_sql_step(step: NotebookStep, job_input: IJobInput) -> bool:
        job_input.execute_query(step.code)
        return True

    @staticmethod
    def run_python_step(step: NotebookStep, job_input: IJobInput) -> bool:
        try:
            sys.path.insert(0, str(step.job_dir))
            filename = step.file_path.name
            success = False
            try:
                log.debug("Loading %s ..." % filename)
                module = types.ModuleType(step.name)
                exec(step.code, module.__dict__)
                log.debug("Loading %s SUCCESS" % filename)
            except BaseException as e:
                log.info("Loading %s FAILURE" % filename)
                errors.log_and_rethrow(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=log,
                    what_happened="Failed loading job sources of %s" % filename,
                    why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                    consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                    countermeasures=errors.MSG_COUNTERMEASURE_FIX_PARENT_EXCEPTION
                    + " Most likely importing a dependency or data job step failed, see"
                    + " logs for details and fix the failed step (details in stacktrace).",
                    exception=e,
                    wrap_in_vdk_error=True,
                )

            for _, func in inspect.getmembers(module, inspect.isfunction):
                if func.__name__ == "run":
                    try:
                        log.info("Entering %s#run(...) ..." % filename)
                        NotebookStepFuncFactory.invoke_run_function(
                            func, job_input, step.name
                        )
                        success = True
                        return True
                    finally:
                        if success:
                            log.info("Exiting  %s#run(...) SUCCESS" % filename)
                            errors.resolvable_context().mark_all_resolved()
                        else:
                            log.error("Exiting  %s#run(...) FAILURE" % filename)
            log.warn(
                "File %s does not contain a valid run() method. Nothing to execute. Skipping %s,"
                + " and continuing with other files (if present).",
                filename,
                filename,
            )
            return success
        finally:
            sys.path.remove(str(step.job_dir))

    @staticmethod
    def invoke_run_function(func: Callable, job_input: IJobInput, step_name: str):
        full_arg_spec = inspect.getfullargspec(func)
        parameter_names = full_arg_spec[0]
        possible_arguments = {
            "job_input": job_input,
        }
        # enable plugins to add different types of job input
        actual_arguments = {
            arg_name: arg_value
            for arg_name, arg_value in possible_arguments.items()
            if arg_name in parameter_names
        }
        if actual_arguments:
            try:
                func(**actual_arguments)
            except SkipRemainingStepsException as e:
                log.debug(e)
                raise e
            except BaseException as e:
                from vdk.internal.builtin_plugins.run.job_input_error_classifier import (
                    whom_to_blame,
                )

                errors.log_and_rethrow(
                    to_be_fixed_by=whom_to_blame(e, __file__, None),
                    log=log,
                    what_happened=f"Data Job step {step_name} completed with error.",
                    why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                    consequences="I will not process the remaining steps (if any), "
                    "and this Data Job execution will be marked as failed.",
                    countermeasures="See exception and fix the root cause, so that the exception does "
                    "not appear anymore.",
                    exception=e,
                    wrap_in_vdk_error=True,
                )
        else:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened=f"I'm trying to call method 'run' and failed.",
                why_it_happened=f"Method is missing at least one job input parameter to be passed",
                consequences="Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                countermeasures="Make sure that you have specified a job input parameter in the signature of the "
                "run method. "
                f"Possible parameters of run function are: {list(possible_arguments.keys())}.",
            )
