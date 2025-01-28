# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    pass
