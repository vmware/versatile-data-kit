# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
import traceback
from dataclasses import dataclass
from typing import Callable

from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors

log = logging.getLogger(__name__)

# consists may duplicates of
# https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/run/file_based_step.py

# The function accept NotebookStep (below class) and IJobInput and
# return true if the step has been executed and false if it is not (valid) executable step.
# On error it's expected to raise an exception.
NotebookStepFunction = Callable[["NotebookStep", IJobInput], bool]


@dataclass
class NotebookStep(Step):
    """
    A notebook step that will be executed when running a data job.

    Step class attributes:
    ::name: str - the name of the concrete step (e.g name of the file)
    ::type: str - string representing a step type (sql or python).
    ::runner_func: StepFunction - function that will execute the actual step
    ::file_path: pathlib.Path - file where the step is defined
    ::job_dir: pathlib.Path - the root job directory
    ::parent: Step | None = None - parent Step

    Additional attributes:
    ::source: str - the code string retrieved from Jupyter code cell
    ::module: module object - the module the code belongs to
    (see imp.new_module in https://docs.python.org/3/library/imp.html)
    """

    def __init__(
        self,
        name,
        type,
        runner_func,
        file_path,
        job_dir,
        source,
        cell_id,
        module=None,
        parent=None,
    ):
        super().__init__(name, type, runner_func, file_path, job_dir, parent)
        self.runner_func = runner_func
        self.source = source
        self.module = module
        self.cell_id = cell_id


class NotebookStepFuncFactory:
    """
    Implementations of runner_func for running Notebook steps
    """

    @staticmethod
    def run_python_step(step: NotebookStep, job_input: IJobInput) -> bool:
        try:
            sys.path.insert(0, str(step.job_dir))
            success = False
            try:
                log.debug("Loading %s ..." % step.name)
                step.module.job_input = job_input
                exec(step.source, step.module.__dict__)
                log.debug("Loading %s SUCCESS" % step.name)
                success = True
            except SyntaxError as e:
                log.info("Loading %s FAILURE" % step.name)
                errors.log_and_rethrow(
                    to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                    log=log,
                    what_happened=f"Failed loading job sources of {step.name} from cell with id:{step.cell_id}"
                    f" from {step.file_path.name}",
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
                    what_happened=f"Failed loading job sources of {step.name} from cell with id:{step.cell_id}"
                    f" from {step.file_path.name}",
                    why_it_happened=f"{e.__class__.__name__} at line {line_number} of {step.name}"
                    f": {e.args[0]}",
                    consequences=f"Current Step {step.name} from {step.file_path}"
                    f"will fail, and as a result the whole Data Job will fail. ",
                    countermeasures=f"Please, check the {step.file_path.name} file again for errors",
                    exception=e,
                    wrap_in_vdk_error=True,
                )
            return success
        finally:
            sys.path.remove(str(step.job_dir))
