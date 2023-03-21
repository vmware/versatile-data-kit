# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple

from vdk.api.plugin.plugin_input import IIngesterPlugin


class ColumnLevelTransformer(ABC):
    def transform(self, destination_table: str, key: str, value: any) -> any:
        pass


class ColumnTransformationIngestorPlugin(IIngesterPlugin):
    """
    When apply from
    """

    IngestionMetadata = NewType("IngestionMetadata", Dict)

    def __init__(self, column_level_transformer: ColumnLevelTransformer):
        self._column_level_transformer = column_level_transformer

    def pre_ingest_process(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: IngestionMetadata = None,
    ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:
        payload = [
            {
                k: self._column_level_transformer.transform(destination_table, k, v)
                for (k, v) in item.items()
            }
            for item in payload
        ]
        return payload, metadata
