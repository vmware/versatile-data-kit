# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import imp
import inspect
import logging
import pathlib
import sys
from typing import Callable
from typing import List

from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors

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
            python_module = imp.load_source(namespace, str(step.file_path))
            success = False
            for _, func in inspect.getmembers(python_module, inspect.isfunction):
                if func.__name__ == "run":
                    try:
                        log.info("Entering %s#run(...) ..." % filename)
                        StepFuncFactory.invoke_run_function(func, job_input)
                        success = True
                        return True
                    finally:
                        if success:
                            log.info("Exiting  %s#run(...) SUCCESS" % filename)
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
    def invoke_run_function(func: Callable, job_input: IJobInput):
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
            func(**actual_arguments)
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
