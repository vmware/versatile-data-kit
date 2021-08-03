# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-ingest-file plugin script.
"""
import logging

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.ingestion_to_file import IngestionToFile


log = logging.getLogger(__name__)


@hookimpl
def initialize_job(context: JobContext) -> None:
    log.info("Initialize data job with IngestFile Plugin.")

    def new_ingester() -> IIngesterPlugin:
        ingester_plugin = IngestionToFile()

        return ingester_plugin

    context.ingester.add_ingester_factory_method("file", new_ingester)
