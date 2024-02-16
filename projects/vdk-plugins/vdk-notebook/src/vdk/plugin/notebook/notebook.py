# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import json
import logging
import pathlib
from pathlib import Path
from typing import List

from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.notebook.cell import Cell
from vdk.plugin.notebook.notebook_based_step import NotebookCellStep
from vdk.plugin.notebook.notebook_based_step import NotebookStepFuncFactory

log = logging.getLogger(__name__)


class JobNotebookLocator:
    """
    Locate the data job files that would be executed by us.
    """

    @staticmethod
    def get_notebook_files(directory: pathlib.Path) -> List[pathlib.Path]:
        """Locates the files in a directory, that are supported for execution.
        Files supported for execution are: .ipynb
        Other files in the directory are ignored.
        :return: List of files from the directory that supported for execution, sorted alphabetically by name.s
        :rtype: :class:`.list`
        """
        script_files = [
            x for x in directory.iterdir() if (x.name.lower().endswith(".ipynb"))
        ]
        script_files.sort(key=lambda x: x.name)
        log.debug(f"Script files of {directory} are {script_files}")
        return script_files


class Notebook:
    """
    Given a notebook file locates the cells with "vdk" tag and saves them.
    Files supported for reading are: ipynb.
    Other cells are ignored.
    """

    @staticmethod
    def register_notebook_steps(file_path: Path, context: JobContext):
        try:
            # see https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
            spec = importlib.util.spec_from_loader("notebook", loader=None)
            python_module = importlib.util.module_from_spec(spec)
            # Used to declare the job_input in the new module
            # Gives access to it: module.job_inut
            # Used to pass the real vdk job_input variable in run_python_step (module.job_input = job_input
            exec("job_input = 1", python_module.__dict__)
            notebook_steps = []
            # see Jupyter json schema here:
            # https://github.com/jupyter/nbformat/blob/main/nbformat/v4/nbformat.v4.schema.json
            content = json.loads(file_path.read_text())
            index = 0
            for jupyter_cell in content["cells"]:
                if jupyter_cell["cell_type"] == "code":
                    cell = Cell(jupyter_cell)
                    if "vdk" in cell.tags:
                        index += 1
                        step = NotebookCellStep(
                            name="".join(
                                [
                                    file_path.name.replace(".ipynb", "_"),
                                    str(index),
                                ]
                            ),
                            type=cell.source_type,
                            runner_func=NotebookStepFuncFactory.get_run_function(
                                cell.source_type
                            ),
                            file_path=file_path,
                            job_dir=context.job_directory,
                            source=cell.source,
                            cell_id=cell.id,
                            module=python_module,
                        )
                        notebook_steps.append(step)
                        context.step_builder.add_step(step)
            context.step_builder._StepBuilder__steps.sort(key=lambda step: step.name)
            log.debug(f"{len(notebook_steps)} " f"cells with vdk tag were detected!")
        except json.JSONDecodeError as e:
            errors.report_and_throw(
                UserCodeError(
                    f"Failed to read the {file_path.name} file.",
                    f"The provided {file_path.name} cannot be loaded into json format and "
                    f"cannot be read as a Jupyter notebook",
                    errors.MSG_CONSEQUENCE_TERMINATING_APP,
                    f"Check the {file_path.name} format again",
                )
            )
