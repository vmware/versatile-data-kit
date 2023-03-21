# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict
from typing import List

from vdk.api.plugin.column_transformation_ingester_plugin import ColumnLevelTransformer
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.plugin.local_differential_privacy.differential_private_unary_encoding import (
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


class UnaryEncodingIngesterPlugin(ColumnLevelTransformer):
    def __init__(
        self,
        unary_encoding_fields: Dict[Table, Dict[Column, DomainOptions]],
        unary_encoding: DifferentialPrivateUnaryEncoding,
    ) -> None:
        self._unary_encoding_fields = unary_encoding_fields
        self._unary_encoding = unary_encoding

    def transform(self, destination_table: str, key: str, value: any):
        table = destination_table if destination_table else ""
        if (
            key
            and table in self._unary_encoding_fields
            and key in self._unary_encoding_fields[table].keys()
            and isinstance(value, str)
        ):
            return self._unary_encoding.privatize(
                value, self._unary_encoding_fields[table][key]
            )
        else:
            return value
