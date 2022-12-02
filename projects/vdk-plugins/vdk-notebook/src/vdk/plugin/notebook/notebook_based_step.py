import inspect
import logging
import pathlib
import sys
import traceback
import importlib.util
from typing import Callable
from typing import List

from vdk.api.job_input import IJobInput
from vdk.internal.core import errors
from vdk.internal.core.errors import SkipRemainingStepsException
from vdk.plugin.notebook.notebook_step import NotebookStep

log = logging.getLogger(__name__)


# consists may duplicates of
# https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/run/file_based_step.py


class JobNotebookLocator:
    """
    Locate the data job files that would be executed by us.
    """

    @staticmethod
    def get_notebook_files(directory: pathlib.Path) -> List[pathlib.Path]:
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
            success = False
            try:
                log.debug("Loading %s ..." % step.name)
                spec = importlib.util.spec_from_loader('nb', loader=None)
                module = importlib.util.module_from_spec(spec)
                exec(step.code, module.__dict__)
                log.debug("Loading %s SUCCESS" % step.name)

                for _, func in inspect.getmembers(module, inspect.isfunction):
                    if func.__name__ == "run":
                        try:
                            log.info("Entering %s#run(...) ..." % step.name)
                            NotebookStepFuncFactory.invoke_run_function(
                                func, job_input, step
                            )
                            success = True
                            return True
                        finally:
                            if success:
                                log.info("Exiting  %s#run(...) SUCCESS" % step.name)
                            else:
                                log.error("Exiting  %s#run(...) FAILURE" % step.name)
                log.warn(
                    "File %s does not contain a valid run() method. Nothing to execute. Skipping %s,"
                    + " and continuing with other files (if present).",
                    step.file_path.name,
                    step.file_path.name,
                )
                return success
            except SyntaxError as e:
                log.info("Loading %s FAILURE" % step.name)
                errors.log_and_rethrow(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=log,
                    what_happened=f"Failed loading job sources of {step.name} from {step.file_path.name}",
                    why_it_happened=f"{e.__class__.__name__} at line {e.lineno} of {step.name}"
                                    f": {e.args[0]}",
                    consequences=f"Current Step {step.name} from {step.file_path}"
                                 f"will fail, and as a result the whole Data Job will fail. ",
                    countermeasures=f"Please, check the {step.file_path.name} file again for syntax errors",
                    exception=e,
                    wrap_in_vdk_error=True,
                )
            except Exception as e:
                cl, exc, tb = sys.exc_info()
                line_number = traceback.extract_tb(tb)[-1][1]
                errors.log_and_rethrow(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=log,
                    what_happened=f"Failed loading job sources of {step.name} from {step.file_path.name}",
                    why_it_happened=f"{e.__class__.__name__} at line {line_number} of {step.name}"
                                    f": {e.args[0]}",
                    consequences=f"Current Step {step.name} from {step.file_path}"
                                 f"will fail, and as a result the whole Data Job will fail. ",
                    countermeasures=f"Please, check the {step.file_path.name} file again for errors",
                    exception=e,
                    wrap_in_vdk_error=True,
                )
        finally:
            sys.path.remove(str(step.job_dir))

    @staticmethod
    def invoke_run_function(func: Callable, job_input: IJobInput, step: NotebookStep):
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
                    what_happened=f"Data Job step {step.name} from  {step.file_path} completed with error.",
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
                consequences=f"Current Step {step.name} from {step.file_path}"
                             f"will fail, and as a result the whole Data Job will fail. ",
                countermeasures="Make sure that you have specified a job input parameter in the signature of the "
                                "run method. "
                                f"Possible parameters of run function are: {list(possible_arguments.keys())}.",
            )
