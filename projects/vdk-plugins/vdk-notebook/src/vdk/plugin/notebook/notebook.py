# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pathlib
from typing import List

from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.plugin.notebook.notebook_based_step import NotebookStepFuncFactory
from vdk.plugin.notebook.notebook_based_step import NotebookStep

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
        :return: List of files from the directory that supported for execution, sorted alphabetically by name.
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

    def __init__(self, file_path: Path):
        try:
            self.sql_and_run_cells = []
            self.python_helper_cells = []
            self.file_path = file_path

            content = json.loads(file_path.read_text())
            cells = [
                cell
                for cell in content["cells"]
                if cell["cell_type"] == "code" and "vdk" in cell["metadata"].get("tags", {})
            ]
            for cell in cells:
                code = "".join(cell["source"])
                if code.startswith("%sql") or "def run(" in code:
                    if code.startswith("%sql"):
                        code = "".join(cell["source"])
                        code.replace(";", "")
                        self.sql_and_run_cells.append([code.replace("%sql", ""), TYPE_SQL])
                    else:
                        self.sql_and_run_cells.append(["".join(cell["source"]), TYPE_PYTHON])
                else:
                    self.python_helper_cells.append("".join(cell["source"]))

        except json.JSONDecodeError as e:
            errors.log_and_rethrow(
                to_be_fixed_by=errors.ResolvableBy.USER_ERROR,
                log=log,
                what_happened=f"Failed to read the {file_path.name} file.",
                why_it_happened=f"The provided {file_path.name} cannot be loaded into json format and "
                                f"cannot be read as a Jupyter notebook",
                consequences=errors.MSG_CONSEQUENCE_TERMINATING_APP,
                countermeasures=f"Check the {file_path.name} format again",
                exception=e,
                wrap_in_vdk_error=True,
            )

    def extract_notebook_steps(self, context: JobContext):
        for index, cell in enumerate(self.sql_and_run_cells):
            if cell[1] == TYPE_SQL:
                step = NotebookStep(
                    name="".join(
                        [
                            self.file_path.name.replace(".ipynb", "_"),
                            str(index),
                        ]
                    ),
                    type=TYPE_SQL,
                    runner_func=NotebookStepFuncFactory.run_sql_step,
                    file_path=self.file_path,
                    job_dir=context.job_directory,
                    code=cell[0],
                )
            else:
                step = NotebookStep(
                    name="".join(
                        [
                            self.file_path.name.replace(".ipynb", "_"),
                            str(index),
                        ]
                    ),
                    type=TYPE_PYTHON,
                    runner_func=NotebookStepFuncFactory.run_python_step,
                    file_path=self.file_path,
                    job_dir=context.job_directory,
                    code="\n".join(self.python_helper_cells) + "\n" + cell[0]
                )
            context.step_builder.add_step(step)
