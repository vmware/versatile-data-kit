# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK-ingest-file plugin script.
"""
import logging
from typing import List
from typing import Optional

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.plugin.ingest_file.ingestion_to_arrow import IngestionToArrowFile
from vdk.plugin.ingest_file.ingestion_to_file import IngestionToFile

log = logging.getLogger(__name__)


class IngestIntoFilePlugin:
    def __init__(self):
        self._file_arrow_ingestion: Optional[IngestionToArrowFile] = None

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.ingester.add_ingester_factory_method("file", lambda: IngestionToFile())

        if self._file_arrow_ingestion is None:
            self._file_arrow_ingestion = IngestionToArrowFile()
            context.ingester.add_ingester_factory_method(
                "file-arrow", lambda: self._file_arrow_ingestion
            )

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int):
        if self._file_arrow_ingestion:
            self._file_arrow_ingestion.close_all()


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(IngestIntoFilePlugin(), "file-ingest")
