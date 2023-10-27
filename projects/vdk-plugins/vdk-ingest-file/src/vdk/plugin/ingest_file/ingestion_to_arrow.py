# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import Dict
from typing import List
from typing import Optional

from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.plugin.ingest_file.arrow_writer import ArrowWriter

log = logging.getLogger(__name__)


class IngestionToArrowFile(IIngesterPlugin):
    """
    Create a new ingestion mechanism to ingest data into local file.
    """

    def __init__(self):
        self._writers: Dict[tuple, ArrowWriter] = dict()

    def close_all(self):
        for writer in self._writers.values():
            writer.close()

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ):
        """
        Ingest payload to file.

        :param payload: List[dict]
            A list of payloads to be ingested.
        :param destination_table: Optional[string]
            Optional argument. A string indicating the table in the database, where
            the data will be ingested.
        :param target: Optional[string]
            Optional argument. Used to specify the name of the file, where the data
            will be ingested.
        :param collection_id: Optional[string]
            Optional argument. Currently not used.
        :param metadata:
            an IngestionMetadata object that contains metadata about the
            pre-ingestion and ingestion operations
        """
        if not target:
            raise ValueError(
                "target cannot be empty. Please specify correct file directory as target"
            )

        if not os.path.exists(target):
            os.mkdir(target)

        if not os.path.isdir(target):
            raise ValueError("target provided must be a directory.")

        key = (target, destination_table)
        writer = self._writers.get(key, None)
        if not writer:
            writer = ArrowWriter(os.path.join(target, destination_table))
            self._writers[key] = writer

        writer.add_payload(payload)
