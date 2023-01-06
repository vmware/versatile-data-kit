# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.notebook.notebook import JobNotebookLocator
from vdk.plugin.notebook.notebook import Notebook

log = logging.getLogger(__name__)


class NotebookPlugin:
    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext):
        file_locator: JobNotebookLocator = JobNotebookLocator()
        notebook_files = file_locator.get_notebook_files(context.job_directory)
        if len(notebook_files) >= 1:
            for file_path in notebook_files:
                nb: Notebook = Notebook(file_path)
                nb.register_notebook_steps(context)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry):
    plugin_registry.load_plugin_with_hooks_impl(NotebookPlugin(), "notebook-plugin")
