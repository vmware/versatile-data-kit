# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.ingestion import ingester_configuration
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.config import ConfigurationBuilder


class IngesterConfigurationPlugin:
    """
    Configuration plugin to ensure all plugin configurations, relevant to ingestion
    plugins are ready when the plugins are loaded.
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        """
        Here we define the configuration settings needed for all ingestion
        plugins with reasonable defaults.
        """
        # Plugin-related configurations
        config_builder.add(
            key="INGEST_METHOD_DEFAULT",
            default_value=None,
            description="Default Ingestion method to be used.",
        )
        config_builder.add(
            key="INGEST_TARGET_DEFAULT",
            default_value=None,
            description="Default Ingestion target to be used.",
        )

        # Configure ingestion specific environment variables
        ingester_configuration.add_definitions(config_builder=config_builder)

    @hookimpl
    def finalize_job(self, context: JobContext) -> None:
        context.ingester.close()
