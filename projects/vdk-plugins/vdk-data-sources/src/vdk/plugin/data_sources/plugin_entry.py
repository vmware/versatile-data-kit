# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.core.config import ConfigurationBuilder

"""
Include the plugins implementation. For example:
"""


class DummyPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        config_builder.add(
            key="dummy_config_key",
            default_value="dummy",
            description="""
                Dummy configuration
            """,
        )


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(DummyPlugin(), "DummyPlugin")
