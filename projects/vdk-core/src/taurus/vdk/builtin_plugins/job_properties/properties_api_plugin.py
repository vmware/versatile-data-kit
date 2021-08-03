# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.job_properties import properties_config
from taurus.vdk.core.config import ConfigurationBuilder


class PropertiesApiPlugin:
    """
    Define the basic configuration needed for Properties API.
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        properties_config.add_definitions(config_builder)
