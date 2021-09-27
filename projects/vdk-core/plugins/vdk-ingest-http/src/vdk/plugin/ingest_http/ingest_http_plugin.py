# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-ingest-file plugin script.
"""
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.ingest_http.ingest_over_http import IngestOverHttp


log = logging.getLogger(__name__)


@hookimpl
def initialize_job(context: JobContext) -> None:
    def new_ingester() -> IIngesterPlugin:
        ingester_plugin = IngestOverHttp()

        return ingester_plugin

    context.ingester.add_ingester_factory_method("http", new_ingester)
