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
            description="""Default Ingestion method to be used. It is
            possible to specify a coma-separated string of ingestion
            plugins, and the payload would be ingested by all plugins
            specified.
            Example:
                INGEST_METHOD_DEFAULT="http"
                and
                INGEST_METHOD_DEFAULT="http,file"
                are both acceptable.
            """,
        )
        config_builder.add(
            key="INGEST_TARGET_DEFAULT",
            default_value=None,
            description="Default Ingestion target to be used.",
        )
        config_builder.add(
            key="INGEST_PAYLOAD_PREPROCESS_SEQUENCE",
            default_value=None,
            description="""A string of coma-separated ingestion pre-processing
            plugin method names, indicating the sequence in which the
            ingestion pre-processing plugins would process the payload. For
            example:
                   INGEST_PAYLOAD_PREPROCESS_SEQUENCE="pre-ingest-process,
                   ingest-pre-process"
            would mean that the payload sent for ingestion would be first
            processed by a `pre-ingest-process` plugin, then by the
            `ingest-pre-process` plugin, and finally would be ingested by
            the ingestion plugin specified by the 'method' argument of the
            send_object_for_ingestion()/send_tabular_data_for_ingestion()
            methods, or specified by the `INGEST_METHOD_DEFAULT` environment
            variable.
            NOTE: If an ingestion plugin implements both pre-processing and
            ingestion logic, it would need to be specified both in
            INGEST_PAYLOAD_PREPROCESS_SEQUENCE and INGEST_METHOD_DEFAULT.
            """,
        )
        config_builder.add(
            key="INGEST_PAYLOAD_POSTPROCESS_SEQUENCE",
            default_value=None,
            description="""A string of coma-separated ingestion post-
            processing plugin method names, indicating the sequence, in which
            the ingestion post-processing plugins would process the metadata
            generated during the ingestion.
            Example:
                    INGEST_PAYLOAD_POSTPROCESS_SEQUENCE="post-ingest-process,
                    post-process"
            The above example shows how the ingestion post-processing plugins
            could be specified. In the example, the metadata generated from
            the ingestion process would be processed first by the
            `post-ingest-process`, and then by the `post-process` plugins.
            NOTE: If an ingestion plugin implements pre-processing, ingestion
            and post-processing logic, it would need to be specified in the
            INGEST_PAYLOAD_PREPROCESS_SEQUENCE, INGEST_METHOD_DEFAULT and
            INGEST_PAYLOAD_POSTPROCESS_SEQUENCE environment variables.
            """,
        )

        # Configure ingestion specific environment variables
        ingester_configuration.add_definitions(config_builder=config_builder)

    @hookimpl
    def finalize_job(self, context: JobContext) -> None:
        context.ingester.close()
