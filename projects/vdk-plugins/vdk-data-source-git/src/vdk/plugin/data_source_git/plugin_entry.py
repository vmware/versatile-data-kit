# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.plugin.data_source_git.git_source import GitDataSource
from vdk.plugin.data_sources.factory import IDataSourceFactory

"""
Include the plugins implementation. For example:
"""


class DataSourceGitPlugin:
    @hookimpl
    def vdk_data_sources_register(self, data_source_factory: IDataSourceFactory):
        data_source_factory.register_data_source_class(GitDataSource)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(DataSourceGitPlugin(), "DataSourceGit")
