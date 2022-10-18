# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.meta_jobs import meta_job_runner

"""
Include the plugins implementation. For example:
"""


class MetaJobsPlugin:
    @hookimpl
    def run_job(self, context: JobContext) -> None:
        # TODO: there should be less hacky way
        meta_job_runner.TEAM_NAME = context.core_context.configuration.get_value(
            JobConfigKeys.TEAM
        )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(MetaJobsPlugin(), "MetaJobsPlugin")
