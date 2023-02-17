# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass
from typing import List
from typing import Optional


@dataclass(frozen=True)
class LineageTable:
    """
    Defines the LineageTable object contract

    Attributes
    catalog: str
        A string holding the catalog where the table lives
    schema: str
        A string holding the schema where the table lives
    table: str
        A string holding the table name
    """

    catalog: Optional[str]
    schema: Optional[str]
    table: str

    def __str__(self):
        s = ""
        if self.catalog:
            s = f"{self.catalog}."
        if self.schema:
            s = f"{s}{self.schema}."
        return f"{s}{self.table}"


@dataclass(frozen=True)
class LineageData:
    """
    Defines the LineageData contract

    Attributes
    query: str
        The original query
    query_type: str
        Type of operation
    query_status: str
        'OK' or 'EXCEPTION'
    input_tables: List[LineageTable]
        An array of LineageTable objects (see LineageTable)
    output_table: LineageTable
        A LineageTable object (see LineageTable)
    """

    query: str
    query_type: str
    query_status: str
    input_tables: List[LineageTable]
    output_table: Optional[LineageTable]
