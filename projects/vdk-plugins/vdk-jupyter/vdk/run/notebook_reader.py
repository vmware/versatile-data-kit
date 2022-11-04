# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from notebook_based_step import NotebookStepFuncFactory
from notebook_step import NotebookStep
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.job_context import JobContext


class NotebookReader:
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
            if cell["source"].startswith("%sql"):
                step = NotebookStep(
                    name=file_path.name,
                    type=TYPE_SQL,
                    runner_func=NotebookStepFuncFactory.run_sql_step,
                    file_path=file_path,
                    job_dir=context.job_directory,
                    code=cell["source"].replace("%sql", ""),
                )
                context.step_builder.add_step(step)
            else:
                python_cells += cell["source"]
                if cell["source"].startswith("def run"):
                    step = NotebookStep(
                        name=file_path.name,
                        type=TYPE_PYTHON,
                        runner_func=NotebookStepFuncFactory.run_python_step,
                        file_path=file_path,
                        job_dir=context.job_directory,
                        code=python_cells,
                    )
                    context.step_builder.add_step(step)
