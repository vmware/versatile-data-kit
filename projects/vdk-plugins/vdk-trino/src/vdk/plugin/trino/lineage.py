# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import List


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

    catalog: str
    schema: str
    table: str

    def __init__(self, catalog: str, schema: str, table: str):
        self.catalog = catalog
        self.schema = schema
        self.table = table


class LineageData:
    """
    Defines the LineageData contract

    Attributes
    query: str
        The original query
    query_type: str
        Type of operation (see below for supported values)
    query_status: str
        'OK' or 'EXCEPTION'
    input_tables: List[LineageTable]
        An array of LineageTable objects (see LineageTable)
    output_table: LineageTable
        A LineageTable object (see LineageTable)

    Supported query_type values are:
        - insert
        - select
        - insert_select
        - rename_table
    """

    query: str
    query_type: str
    query_status: str
    input_tables: List[LineageTable]
    output_table: LineageTable

    def __init__(
        self,
        query: str,
        query_type: str,
        query_status: str,
        input_tables: List[LineageTable],
        output_table: LineageTable,
    ):
        self.query = query
        self.query_type = query_type
        self.query_status = query_status
        self.input_tables = input_tables
        self.output_table = output_table


class LineageLogger(ABC):
    """
    This interface describes what behaviour a lineage logger must possess to interact with the lineage logging
    functionality afforded by vdk-trino.
    """

    def send(self, lineage_data: LineageData) -> None:
        """
        This method sends the collected lineage data to some lineage data processing application.

        :param lineage_data: The collected lineage data.
        """
        pass
