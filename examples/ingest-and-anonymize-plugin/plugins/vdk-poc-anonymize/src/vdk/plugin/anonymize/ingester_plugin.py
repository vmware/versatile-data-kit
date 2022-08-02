# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.plugin.anonymize.anonymizer import Anonymizer

IngestionMetadata = IIngesterPlugin.IngestionMetadata

log = logging.getLogger(__name__)


"""
Ingester Plugins are implemented by inheriting IIngesterPlugin and impelemented only the needed methods.
See IIngesterPlugin docs for more info.
"""


class AnonymizationIngesterPlugin(IIngesterPlugin):
    def __init__(
        self, anonymization_fields: Dict[str, List[str]], anonymizer: Anonymizer
    ) -> None:
        self._anonymization_fields = anonymization_fields
        self._anonymizer = anonymizer

    def _anonymize_if_needed(self, destination_table: str, key: str, value: Any):
        table = destination_table if destination_table else ""
        if (
            key
            and table in self._anonymization_fields
            and key in self._anonymization_fields[table]
        ):
            return self._anonymizer.anonymize(value)
        else:
            return value

    # inherited
    def pre_ingest_process(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: IngestionMetadata = None,
    ) -> Tuple[List[Dict], Optional[IngestionMetadata]]:

        if self._anonymization_fields:
            payload = [
                {
                    k: self._anonymize_if_needed(destination_table, k, v)
                    for (k, v) in item.items()
                }
                for item in payload
            ]
        return payload, metadata
