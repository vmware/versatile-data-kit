# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.internal.control.plugin.control_plugin_manager import Plugins

log = logging.getLogger(__name__)


class DefaultOptions:
    def __init__(self, plugins: Plugins):
        self.plugins = plugins

    def get_default_map(self):
        default_map = self.plugins.hook().get_default_commands_options()
        return default_map
