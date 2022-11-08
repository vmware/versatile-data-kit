# Copyright
# 2022
# VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.jupyter.notebook_based_step import JobNotebookLocator
from vdk.plugin.jupyter.notebook_reader import NotebookReader
from vdk.internal.core.config import ConfigurationBuilder

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
        notebook_reader: NotebookReader = NotebookReader()
        for file_path in notebook_files:
            notebook_reader.read_notebook_and_save_steps(file_path, context)
