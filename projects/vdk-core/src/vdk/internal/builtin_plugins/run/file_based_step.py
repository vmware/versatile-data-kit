# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import inspect
import logging
import pathlib
import sys
from typing import Callable
from typing import List

from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors
from vdk.internal.core.errors import SkipRemainingStepsException

log = logging.getLogger(__name__)

TYPE_SQL = "sql"
TYPE_PYTHON = "python"


class JobFilesLocator:
    """
    Locate the data job files that would be executed by us.
    """

    def get_script_files(self, directory: pathlib.Path) -> List[pathlib.Path]:
        """Locates the files in a directory, that are supported for execution.

        Files supported for execution are: .sql and .py
        Other files in the directory are ignored.

        :return: List of files from the directory that supported for execution, sorted alphabetically by name.
        :rtype: :class:`.list`

        """
        script_files = [
            x
            for x in directory.iterdir()
            if (x.name.lower().endswith(".sql") or x.name.lower().endswith(".py"))
        ]
        script_files.sort(key=lambda x: x.name)
        log.debug(f"Script files of {directory} are {script_files}")
        return script_files


class StepFuncFactory:
    """
    Implementations of runner_func for running steps
    """

    @staticmethod
    def run_sql_step(step: Step, job_input: IJobInput) -> bool:
        """ """
        with open(step.file_path, encoding="utf8") as sql_file:
            sql = sql_file.read()
        job_input.execute_query(sql)
        return True

    @staticmethod
    def run_python_step(step: Step, job_input: IJobInput) -> bool:
        """Runs a Python step script.

        In order for a Python file to be executed as a Job Step, it must follow the contract of having:

        def run(job_input)

        method defined, which is the starting point of the Step.

        :return: True if there was a run(job_input) method to run, False otherwise
        :rtype: :class:`.bool`
        """

        try:
            sys.path.insert(0, str(step.job_dir))
            filename = step.file_path.name
            namespace = "step_" + str(filename).lower().strip(".py")
            success = False

            try:
                log.debug("Loading %s ..." % filename)
                spec = importlib.util.spec_from_file_location(
                    namespace, str(step.file_path)
                )
                python_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(python_module)
                log.debug("Loading %s SUCCESS" % filename)
            except BaseException as e:
                log.info("Loading %s FAILURE" % filename)
                log.error(
                    "\n".join(
                        [
                            "Failed loading job sources of %s" % filename,
                            errors.MSG_WHY_FROM_EXCEPTION(e),
                            " Most likely importing a dependency or data job step failed, see"
                            + " logs for details and fix the failed step.",
                        ]
                    )
                )
                errors.report(errors.ResolvableBy.USER_ERROR, e)
                raise e

            for _, func in inspect.getmembers(python_module, inspect.isfunction):
                if func.__name__ == "run":
                    try:
                        log.info("Entering %s#run(...) ..." % filename)
                        StepFuncFactory.invoke_run_function(func, job_input, step.name)
                        success = True
                        return True
                    finally:
                        if success:
                            log.info("Exiting  %s#run(...) SUCCESS" % filename)
                            errors.resolvable_context().mark_all_resolved()
                        else:
                            log.error("Exiting  %s#run(...) FAILURE" % filename)
            log.warning(
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
        # https://docs.python.org/3/library/inspect.html#inspect.getfullargspec
        full_arg_spec = inspect.getfullargspec(func)
        parameter_names = full_arg_spec[0]
        #  if 'job_input' not in argument_names: TODO: what should happen ? What is the behaviour in SC
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
                # Catch and rethrow exception here since it is handled at
                # the run_step() hook level. We also don't want to use the
                # errors.log_and_rethrow() method since it will log a
                # confusing message to the users.
                log.debug(e)
                raise e
            except BaseException as e:
                from vdk.internal.builtin_plugins.run.job_input_error_classifier import (
                    whom_to_blame,
                )

                to_be_fixed_by = whom_to_blame(e, __file__, None)
                errors.report(to_be_fixed_by, e)
                raise e
        else:
            errors.report_and_throw(
                errors.UserCodeError(
                    "I'm trying to call method 'run' and failed.",
                    "Method is missing at least one job input parameter to be passed",
                    "Current Step (python file) will fail, and as a result the whole Data Job will fail. ",
                    "Make sure that you have specified a job input parameter in the signature of the "
                    "run method. "
                    f"Possible parameters of run function are: {list(possible_arguments.keys())}.",
                )
            )
