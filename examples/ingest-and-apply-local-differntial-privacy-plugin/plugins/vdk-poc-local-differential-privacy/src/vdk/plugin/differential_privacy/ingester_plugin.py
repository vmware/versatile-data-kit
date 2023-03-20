# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.plugin.differential_privacy.differential_private_random_response import (
    DifferentialPrivateRandomResponse,
)
from vdk.plugin.differential_privacy.differential_private_unary_encoding import (
    DifferentialPrivateUnaryEncoding,
)

IngestionMetadata = IIngesterPlugin.IngestionMetadata

log = logging.getLogger(__name__)

"""
Ingester Plugins are implemented by inheriting IIngesterPlugin and impelemented only the needed methods.
See IIngesterPlugin docs for more info.
"""

Table = str
Column = str
DomainOptions = List[str]


class DifferentialPrivacyIngesterPlugin(IIngesterPlugin):
    def __init__(
        self,
        random_response_fields: Dict[Table, List[Column]],
        unary_encoding_fields: Dict[Table, Dict[Column, DomainOptions]],
    ) -> None:
        self._random_response_fields = random_response_fields
        self._unary_encoding_fields = unary_encoding_fields

    def _privatize_if_needed(self, destination_table: str, key: str, value: any):
        table = destination_table if destination_table else ""
        if key:
            if (
                table in self._random_response_fields
                and key in self._random_response_fields[table]
                and isinstance(value, bool)
            ):
                return DifferentialPrivateRandomResponse().privatize(value)
            elif (
                table in self._unary_encoding_fields
                and key in self._unary_encoding_fields[table].keys()
                and isinstance(value, str)
            ):
                return DifferentialPrivateUnaryEncoding().privatize(
                    value, self._unary_encoding_fields[table][key]
                )
            else:
                return value
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
        if self._random_response_fields:
            payload = [
                {
                    k: self._privatize_if_needed(destination_table, k, v)
                    for (k, v) in item.items()
                }
                for item in payload
            ]
        return payload, metadata
