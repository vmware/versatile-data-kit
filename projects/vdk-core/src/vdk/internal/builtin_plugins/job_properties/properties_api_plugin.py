# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.job_properties import properties_config
from vdk.internal.builtin_plugins.job_properties.inmemproperties import (
    InMemPropertiesServiceClient,
)
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder


class PropertiesApiPlugin:
    """
    Define the basic configuration needed for Properties API.
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        properties_config.add_definitions(config_builder)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.properties.set_properties_factory_method(
            "memory", lambda: InMemPropertiesServiceClient()
        )
