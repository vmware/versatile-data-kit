# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
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
                Notebook.register_notebook_steps(file_path, context)

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> None:
        out: HookCallResult
        out = yield
        result: ExecutionResult = out.get_result()
        step_results = result.steps_list
        for step_result in step_results:
            if step_result.status == ExecutionStatus.ERROR:
                error_info = {
                    "step_name": step_result.name,
                    "blamee": step_result.blamee.value.__str__(),
                    "details": step_result.details,
                }
                output_path = (
                    context.job_directory.parent / f".{result.data_job_name}_error.json"
                )
                with open(output_path, "w") as outfile:
                    outfile.write(json.dumps(error_info))


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry):
    plugin_registry.load_plugin_with_hooks_impl(NotebookPlugin(), "notebook-plugin")
