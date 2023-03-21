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
    def transform(self, destination_table: str, column_name: str, column_value: any) -> any:
        """
        :return: The value to be stored in the column.
        If the transformer doesn't want to make any changes it should return the existing value
        """
        pass


class ColumnTransformationIngestorPlugin(IIngesterPlugin):
    """
    Often transformations need to be preformed on data before ingesting it.
    These transformations often operate on a single row and single column at a time.
    As a result many ingestion plugins duplicate the work of iterating over all values.

    This class iterates over all values allowing plugin code to focus on what needs to be done and removes duplication
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
