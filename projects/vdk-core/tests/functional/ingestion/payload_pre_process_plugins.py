# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext


log = logging.getLogger(__name__)


class ConvertPayloadValuesToString(IIngesterPlugin):
    def pre_ingest_process(
        self, payload: List[dict], metadata: IIngesterPlugin.IngestionMetadata = None
    ) -> List[dict]:
        return [{k: str(v) for (k, v) in i.items()} for i in payload]

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with ConvertPayloadValuesToString Plugin.")

        context.ingester.add_ingester_factory_method("convert-to-string", lambda: self)


class AddPayloadSizeAsColumn(IIngesterPlugin):
    def pre_ingest_process(
        self, payload: List[dict], metadata: IIngesterPlugin.IngestionMetadata = None
    ) -> List[dict]:
        processed_payloads = []
        for i in payload:
            payload_size = sys.getsizeof(str(i))
            i["payload_size"] = payload_size
            processed_payloads.append(i)

        return processed_payloads

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with ConvertPayloadValuesToString Plugin.")

        context.ingester.add_ingester_factory_method("add-payload-size", lambda: self)
