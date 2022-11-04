# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging

from notebook_based_step import JobNotebookLocator
from notebook_reader import NotebookReader
from notebook_step import NotebookStepBuilder
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder

log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key="my_config",
        default_value="default-value-to-use-if-not-set-later",
        description="Description of my config.",
    )


@hookimpl
def run_job(self, context: JobContext):
    # just for testing
    value = context.configuration.get_required_option("my_config")
    log.info("\nbar\n")


@hookimpl
def initialize_job(context: JobContext):
    context.step_builder = NotebookStepBuilder()
    if context.job_directory is None:
        log.info(
            "Data Job directory is not specified. Default job initialization will be skipped."
        )
        return

    file_locator: JobNotebookLocator = JobNotebookLocator()
    notebook_files = file_locator.get_notebook_files(context.job_directory)
    notebook_reader: NotebookReader = NotebookReader()

    for file_path in notebook_files:
        notebook_reader.read_notebook_and_save_steps(file_path, context)
