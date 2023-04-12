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
        """
        Sets the DAGs plugin configuration and other parameters.

        :param context: the job context
        :return:
        """
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
        Adds the DAG-related configuration variables.

        :param config_builder: the builder used to add the configuration variables
        :return:
        """
        add_definitions(config_builder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    """
    Loads the DAGs plugin.

    :param plugin_registry: plugin registry used to register the plugin and its hooks
    :param command_line_args: a list of command line args passed to VDK
    :return:
    """
    plugin_registry.load_plugin_with_hooks_impl(MetaJobsPlugin(), "MetaJobsPlugin")
