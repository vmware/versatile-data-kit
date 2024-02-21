# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
import traceback
from dataclasses import dataclass
from typing import Callable
from typing import Union

from vdk.api.job_input import IJobInput
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.notebook import vdk_ingest
from vdk.plugin.notebook.vdk_ingest import TYPE_INGEST

log = logging.getLogger(__name__)

# consists may duplicates of
# https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-core/src/vdk/internal/builtin_plugins/run/file_based_step.py

# The function accept NotebookCellStep (below class) and IJobInput and
# return true if the step has been executed and false if it is not (valid) executable step.
# On error it's expected to raise an exception.
NotebookStepFunction = Callable[["NotebookCellStep", IJobInput], bool]


@dataclass
class NotebookCellStep(Step):
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
    def get_run_function(source_type: Union[TYPE_PYTHON, TYPE_SQL]) -> Callable:
        if source_type == TYPE_PYTHON:
            return NotebookStepFuncFactory.run_python_step
        elif source_type == TYPE_SQL:
            return NotebookStepFuncFactory.run_sql_step
        elif source_type == TYPE_INGEST:
            return vdk_ingest.run_ingest_step
        else:
            raise NotImplementedError(
                f"Run function for source type {source_type} is not implemented."
            )

    @staticmethod
    def run_sql_step(step: NotebookCellStep, job_input: IJobInput) -> bool:
        """ """
        job_input.execute_query(step.source)
        return True

    @staticmethod
    def run_python_step(step: NotebookCellStep, job_input: IJobInput) -> bool:
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
                errors.report_and_throw(
                    UserCodeError(
                        f"Failed loading job sources of {step.name} from cell with cell_id:{step.cell_id}"
                        f" from {step.file_path.name}",
                        f"{e.__class__.__name__} at line {e.lineno} of {step.name}"
                        f": {e.args[0]}",
                        f"Current Step {step.name} from {step.file_path}"
                        "will fail, and as a result the whole Data Job will fail. ",
                        f"Please, check the {step.file_path.name} file again for syntax errors",
                        f"{e}",
                    )
                )
            except Exception as e:
                cl, exc, tb = sys.exc_info()
                line_number = traceback.extract_tb(tb)[-1][1]
                errors.report_and_throw(
                    UserCodeError(
                        f"Failed loading job sources of {step.name} from cell with cell_id:{step.cell_id}"
                        f" from {step.file_path.name}",
                        f"{e.__class__.__name__} at line {line_number} of {step.name}"
                        f": {e.args[0]}",
                        f"Current Step {step.name} from {step.file_path}"
                        "will fail, and as a result the whole Data Job will fail. ",
                        f"Please, check the {step.file_path.name} file again for errors",
                        f"{e}",
                    )
                )
            return success
        finally:
            sys.path.remove(str(step.job_dir))
