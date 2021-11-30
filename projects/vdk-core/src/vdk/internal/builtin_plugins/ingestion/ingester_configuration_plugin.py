# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.ingestion import ingester_configuration
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder


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
        config_builder.add(
            key="INGEST_PLUGIN_PROCESS_SEQUENCE",
            default_value=None,
            description="""A string of coma-separated ingestion plugin method names,
            indicating the sequence in which the ingestion plugins would process the
            payload. For example:
                   INGEST_PLUGIN_PROCESS_SEQUENCE="pre-ingest-process,http"
            would mean that the payload sent for ingestion would be first processed by
            a `pre-ingest-process` plugin, before being ingested using the `ingest-http`
            plugin.
            NOTE: The value of this environment variable takes precedence
            over the value in the `INGEST_METHOD_DEFAULT` environment
            variable, i.e., if both variables are set, the value of
            `INGEST_METHOD_DEFAULT` would be ignored. If, however, a method
            argument is passed to the send_object_for_ingestion(
            )/send_tabular_data_for_ingestion() methods, this argument would be
            considered as the last ingestion plugin in the sequence to
            process the payload.
            """,
        )

        # Configure ingestion specific environment variables
        ingester_configuration.add_definitions(config_builder=config_builder)

    @hookimpl
    def finalize_job(self, context: JobContext) -> None:
        context.ingester.close()
