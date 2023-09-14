# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.plugin.sql_extensions.sql_splitter import SqlStepSplitterPlugin


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    """
    Here we register all (sql-extensions) plugins.
    Each plugin have its own separate file and class where its logic it is
    """
    plugin_registry.load_plugin_with_hooks_impl(
        SqlStepSplitterPlugin(), "SqlStepSplitterPlugin"
    )
