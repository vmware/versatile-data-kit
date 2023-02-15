# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import logging
import sys
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext


log = logging.getLogger(__name__)
IngestionMetadata = IIngesterPlugin.IngestionMetadata


class ConvertPayloadValuesToString(IIngesterPlugin):
    def pre_ingest_process(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: IngestionMetadata = None,
    ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:
        processed_payload = [{k: str(v) for (k, v) in i.items()} for i in payload]
        return processed_payload, metadata

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with ConvertPayloadValuesToString Plugin.")

        context.ingester.add_ingester_factory_method("convert-to-string", lambda: self)


class AddPayloadSizeAsColumn(IIngesterPlugin):
    @dataclass
    class Payload:
        payload: List[dict]
        destination_table: Optional[str]
        target: Optional[str]
        collection_id: Optional[str]

    def __init__(self):
        self.payloads: List[AddPayloadSizeAsColumn.Payload] = []

    # Do payload pre-processing
    def pre_ingest_process(
        self,
        payload: List[dict],
        metadata: IngestionMetadata = None,
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:
        processed_payloads = []
        start_time = datetime.datetime(year=2022, month=1, day=27, hour=16)
        metadata = IngestionMetadata({"ingestion_submission_start_time": start_time})
        for i in payload:
            payload_size = sys.getsizeof(str(i))
            i["payload_size"] = payload_size
            processed_payloads.append(i)

        return processed_payloads, metadata

    # Ingest pre-processed payload
    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestionMetadata] = None,
    ):
        self.payloads.append(
            AddPayloadSizeAsColumn.Payload(
                payload, destination_table, target, collection_id
            )
        )

    # Process ingestion metadata
    def post_ingest_process(
        self,
        payload: Optional[List[dict]] = None,
        metadata: Optional[IngestionMetadata] = None,
        exception: Optional[Exception] = None,
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> Optional[IngestionMetadata]:
        start_time = None
        if metadata:
            start_time = metadata.get("ingestion_submission_start_time")

        try:
            end_time = start_time + datetime.timedelta(seconds=90)
            metadata["ingestion_submission_start_time"] = end_time
        except TypeError:
            pass

        return metadata

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with ConvertPayloadValuesToString Plugin.")

        context.ingester.add_ingester_factory_method("add-payload-size", lambda: self)


class DummyIngestionPlugin(IIngesterPlugin):
    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestionMetadata] = None,
    ):
        log.info("Calling dummy ingest_payload() method.")

    @hookimpl(tryfirst=True)
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with DummyIngestion Plugin.")

        context.ingester.add_ingester_factory_method("dummy-ingest", lambda: self)
