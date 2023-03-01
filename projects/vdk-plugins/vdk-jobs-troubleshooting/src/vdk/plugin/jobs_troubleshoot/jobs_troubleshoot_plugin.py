# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-JOBS-TROUBLESHOOTING plugin script.
"""
import logging
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.jobs_troubleshoot.api.troubleshoot_utility import ITroubleshootUtility
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import add_definitions
from vdk.plugin.jobs_troubleshoot.troubleshoot_utilities.utilities_registry import (
    get_utilities_to_use,
)

log = logging.getLogger(__name__)


class JobTroubleshootingPlugin:
    """
    Entrypoint for the Data Jobs Troubleshooting plugin - it provides the means to initialize and configure
    troubleshooting utilities, based on the configured environment variables.

    Example:
    To start the thread dump utility, configure the following environment variables:
        VDK_TROUBLESHOOT_UTILITIES_TO_USE="thread-dump"
        VDK_PORT_TO_USE=8783
    """

    def __init__(self):
        self.troubleshooting_utils: List[ITroubleshootUtility] = []

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder=config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        self.troubleshooting_utils = get_utilities_to_use(
            job_config=context.core_context.configuration
        )
        try:
            for util in self.troubleshooting_utils:
                util.start()
        except Exception as e:
            log.info(
                f"""
                An exception occurred while starting a troubleshooting
                utility. The error was: {e}
                """
            )

    @hookimpl
    def finalize_job(self, context: JobContext) -> None:
        try:
            for util in self.troubleshooting_utils:
                util.stop()
        except Exception as e:
            log.info(
                f"""
                An exception occurred while stopping a troubleshooting
                utility. The error was: {e}
                """
            )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List) -> None:
    plugin_registry.load_plugin_with_hooks_impl(
        JobTroubleshootingPlugin(), "job-troubleshooting-plugin"
    )
