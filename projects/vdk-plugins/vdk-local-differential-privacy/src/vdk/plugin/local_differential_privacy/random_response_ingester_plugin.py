# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict
from typing import List

from vdk.api.plugin.column_transformation_ingester_plugin import ColumnLevelTransformer
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.plugin.local_differential_privacy.differential_private_random_response import (
    DifferentialPrivateRandomResponse,
)

IngestionMetadata = IIngesterPlugin.IngestionMetadata

log = logging.getLogger(__name__)
Table = str
Column = str
DomainOptions = List[str]


class RandomResponseIngesterPlugin(ColumnLevelTransformer):
    """
    Responsible for hooking DifferentialPrivateRandomResponse into the VDK framework
    """
    def __init__(
        self,
        random_response_fields: Dict[Table, List[Column]],
        random_response: DifferentialPrivateRandomResponse,
    ) -> None:
        self._random_response_fields = random_response_fields
        self._random_response = random_response

    def transform(self, destination_table: str, key: str, value: any):
        table = destination_table if destination_table else ""
        if (
            key
            and table in self._random_response_fields
            and key in self._random_response_fields[table]
            and isinstance(value, bool)
        ):
            return self._random_response.privatize(value)
        else:
            return value
