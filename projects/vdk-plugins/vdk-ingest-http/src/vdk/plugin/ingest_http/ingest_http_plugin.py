# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-ingest-file plugin script.
"""
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.ingest_http.ingest_over_http import IngestOverHttp

log = logging.getLogger(__name__)


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """
    Here we define what configuration settings are needed for the Ingest HTTP plugin with reasonable defaults
    """
    config_builder.add(
        key="INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES",
        default_value=None,
        description="When the payload size exceeds this optional integer threshold, then gzip compression is applied",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_COMPRESSION_ENCODING",
        default_value="utf-8",
        description="Encoding used if compressing the payload",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    def new_ingester() -> IIngesterPlugin:
        ingester_plugin = IngestOverHttp(context)

        return ingester_plugin

    context.ingester.add_ingester_factory_method("http", new_ingester)
