# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.meta_jobs import meta_job_runner
from vdk.plugin.meta_jobs.meta_configuration import add_definitions
from vdk.plugin.meta_jobs.meta_configuration import MetaPluginConfiguration


class MetaJobsPlugin:
    @staticmethod
    @hookimpl
    def run_job(context: JobContext) -> None:
        # TODO: there should be less hacky way
        meta_job_runner.TEAM_NAME = context.core_context.configuration.get_value(
            JobConfigKeys.TEAM
        )
        meta_job_runner.META_CONFIG = MetaPluginConfiguration(
            context.core_context.configuration
        )

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        """
        Here we define what configuration settings are needed for DAGs with reasonable defaults.
        """
        add_definitions(config_builder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(MetaJobsPlugin(), "MetaJobsPlugin")
