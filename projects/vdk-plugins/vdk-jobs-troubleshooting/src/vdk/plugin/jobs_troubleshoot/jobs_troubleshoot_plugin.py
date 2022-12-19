# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-JOBS-TROUBLESHOOTING plugin script.
"""
import logging
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.jobs_troubleshoot.troubleshoot_configuration import add_definitions

log = logging.getLogger(__name__)


class JobTroubleshootingPlugin:
    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder=config_builder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List) -> None:
    plugin_registry.load_plugin_with_hooks_impl(
        JobTroubleshootingPlugin(), "job-troubleshooting-plugin"
    )
