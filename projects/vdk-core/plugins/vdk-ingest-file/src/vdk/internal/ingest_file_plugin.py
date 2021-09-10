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
from vdk.internal.ingestion_to_file import IngestionToFile


log = logging.getLogger(__name__)


@hookimpl
def initialize_job(context: JobContext) -> None:
    log.info("Initialize data job with IngestFile Plugin.")

    def new_ingester() -> IIngesterPlugin:
        ingester_plugin = IngestionToFile()

        return ingester_plugin

    context.ingester.add_ingester_factory_method("file", new_ingester)
