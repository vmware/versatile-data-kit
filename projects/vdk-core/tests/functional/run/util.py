# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from typing import List
from typing import Optional

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.context import CoreContext
from vdk.plugin.test_utils.util_funcs import get_test_job_path


def job_path(job_name: str) -> str:
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))), job_name
    )


class HookCallTracker:
    @property
    def calls(self):
        return self._calls

    def __init__(self):
        self._calls = []

    @hookimpl
    def vdk_start(
        self, plugin_registry: IPluginRegistry, command_line_args: List
    ) -> None:
        self._calls.append("vdk_start")

    @hookimpl
    def vdk_command_line(self, root_command: click.Group) -> None:
        self._calls.append("vdk_command_line")

    @hookimpl
    def vdk_configure(self, config_builder: "ConfigurationBuilder") -> None:
        self._calls.append("vdk_configure")

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        self._calls.append("vdk_initialize")

    @hookimpl
    def vdk_exception(self, exception: Exception) -> bool:
        self._calls.append("vdk_exception")

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int) -> None:
        self._calls.append("vdk_exit")

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self._calls.append("initialize_job")

    @hookimpl
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        self._calls.append("run_job")

    @hookimpl
    def run_step(self, context: JobContext, step: Step) -> Optional[StepResult]:
        self._calls.append("run_step")

    @hookimpl
    def finalize_job(self, context: JobContext) -> None:
        self._calls.append("finalize_job")
