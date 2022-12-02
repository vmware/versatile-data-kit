
from __future__ import annotations

import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext

from vdk.plugin.notebook.notebook_based_step import JobNotebookLocator
from vdk.plugin.notebook.notebook_reader import NotebookReader
from vdk.plugin.notebook.notebook_reader import Notebook
log = logging.getLogger(__name__)


@hookimpl()
def initialize_job(context: JobContext):
    if context.job_directory is None:
        log.info(
            "Data Job directory is not specified. Default job initialization will be skipped."
        )
        return
    file_locator: JobNotebookLocator = JobNotebookLocator()
    notebook_files = file_locator.get_notebook_files(context.job_directory)
    if len(notebook_files) >= 1:
        for file_path in notebook_files:
            nb: Notebook = Notebook(file_path)
            NotebookReader.read_notebook_and_save_steps(nb, context)
