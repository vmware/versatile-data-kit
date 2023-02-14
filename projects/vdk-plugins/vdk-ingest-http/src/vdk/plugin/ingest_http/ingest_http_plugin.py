# Copyright 2021-2023 VMware, Inc.
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
        key="INGEST_OVER_HTTP_CONNECT_TIMEOUT_SECONDS",
        default_value=None,
        description="How many seconds to wait for connecting to the server",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_READ_TIMEOUT_SECONDS",
        default_value=None,
        description="How many seconds to wait for the server to read data",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_VERIFY",
        default_value=True,
        description="Either a boolean, in which case it controls whether we verify "
        "the server's TLS certificate, or a string, in which case it must be a path "
        "to a CA bundle to use. Defaults to ``True``",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_CERT_FILE_PATH",
        default_value=None,
        description="Path to SSL client cert file (.pem)",
    )
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
    config_builder.add(
        key="INGEST_OVER_HTTP_RETRY_TOTAL",
        default_value=10,
        description="Total number of retries to allow. Takes precedence over other counts.",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_RETRY_BACKOFF_FACTOR",
        default_value=0.0,
        description="A backoff factor to apply between attempts after the second try "
        "(most errors are resolved immediately by a second try without a "
        "delay). urllib3 will sleep for:: "
        "{backoff factor} * (2 ** ({number of total retries} - 1))",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_RETRY_STATUS_FORCELIST",
        default_value=None,
        description="A string of comma-separated HTTP status codes that we should force a retry on.",
    )
    config_builder.add(
        key="INGEST_OVER_HTTP_ALLOW_NAN",
        default_value=False,
        description="If set to False, then it will be a ``ValueError`` to serialize out of range ``float`` "
        "values (``nan``, ``inf``, ``-inf``) in strict compliance of the JSON specification, "
        "instead of using the JavaScript equivalents (``NaN``, ``Infinity``, ``-Infinity``).",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    def new_ingester() -> IIngesterPlugin:
        ingester_plugin = IngestOverHttp(context)

        return ingester_plugin

    context.ingester.add_ingester_factory_method("http", new_ingester)
