# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path

from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.jupyter.notebook_step import NotebookStep
from vdk.plugin.jupyter.notebook_based_step import NotebookStepFuncFactory
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL


class NotebookReader:
    """
       Given a notebook file locates the cells with "vdk" tag and creates NotebookSteps by them.
       Files supported for reading are: ipynb.
       Other cells are ignored.
       """
    @staticmethod
    def read_notebook_and_save_steps(file_path: Path, context: JobContext):
        content = json.loads(file_path.read_text())
        cells = [
            cell
            for cell in content["cells"]
            if cell["cell_type"] == "code" and "vdk" in cell["metadata"].get("tags", {})
        ]
        python_cells = ""
        for cell in cells:
            if cell["source"][0].startswith("%sql"):
                code = ''.join(cell["source"])
                code.replace(';', '')
                step = NotebookStep(
                    name=file_path.name,
                    type=TYPE_SQL,
                    runner_func=NotebookStepFuncFactory.run_sql_step,
                    file_path=file_path,
                    job_dir=context.job_directory,
                    code=code.replace('%sql', '')
                )
                context.step_builder.add_step(step)
            else:
                python_cells += ('\n' + ''.join(cell["source"]))
                if cell["source"][0].startswith("def run"):
                    step = NotebookStep(
                        name=file_path.name,
                        type=TYPE_PYTHON,
                        runner_func=NotebookStepFuncFactory.run_python_step,
                        file_path=file_path,
                        job_dir=context.job_directory,
                        code=python_cells
                    )
                    context.step_builder.add_step(step)
