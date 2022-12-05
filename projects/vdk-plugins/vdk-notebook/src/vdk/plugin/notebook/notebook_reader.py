import json
import logging
from pathlib import Path

from vdk.internal.builtin_plugins.run.file_based_step import TYPE_PYTHON
from vdk.internal.builtin_plugins.run.file_based_step import TYPE_SQL
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors

from vdk.plugin.notebook.notebook_based_step import NotebookStepFuncFactory
from vdk.plugin.notebook.notebook_step import NotebookStep

log = logging.getLogger(__name__)


class Notebook:
    """
        Given a notebook file locates the cells with "vdk" tag and saves them.
        Files supported for reading are: ipynb.
        Other cells are ignored.
        """

    def __init__(self, file_path: Path):
        try:
            content = json.loads(file_path.read_text())
            self.cells = [
                cell
                for cell in content["cells"]
                if cell["cell_type"] == "code" and "vdk" in cell["metadata"].get("tags", {})
            ]
            self.file_path = file_path
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


class NotebookReader:
    @staticmethod
    def read_notebook_and_save_steps(notebook: Notebook, context: JobContext):
        python_cells = ""
        step_index = 0
        for cell in notebook.cells:
            if cell["source"][0].startswith("%sql"):
                code = "".join(cell["source"])
                code.replace(";", "")
                step = NotebookStep(
                    name="".join([notebook.file_path.name.replace(".ipynb", '_'), str(step_index)]),
                    type=TYPE_SQL,
                    runner_func=NotebookStepFuncFactory.run_sql_step,
                    file_path=notebook.file_path,
                    job_dir=context.job_directory,
                    code=code.replace("%sql", ""),
                )
                step_index += 1
                context.step_builder.add_step(step)
            else:
                python_cells += "\n" + "".join(cell["source"])
                if "def run(job_input" in cell["source"][0]:
                    step = NotebookStep(
                        name="".join([notebook.file_path.name.replace(".ipynb", '_'), str(step_index)]),
                        type=TYPE_PYTHON,
                        runner_func=NotebookStepFuncFactory.run_python_step,
                        file_path=notebook.file_path,
                        job_dir=context.job_directory,
                        code=python_cells,
                    )
                    step_index += 1
                    context.step_builder.add_step(step)
