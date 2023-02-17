# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json

from vdk.plugin.trino.lineage_utils import _get_input_tables_from_explain
from vdk.plugin.trino.lineage_utils import _get_lineage_table_from_plan
from vdk.plugin.trino.lineage_utils import _lineage_table_from_name
from vdk.plugin.trino.lineage_utils import get_rename_table_lineage_from_query
from vdk.plugin.trino.lineage_utils import is_heartbeat_query


def test_is_heartbeat_query():
    assert is_heartbeat_query("select 1")
    assert is_heartbeat_query("select 'aaa'")
    assert not is_heartbeat_query("select * from a_table")


def test_lineage_table_from_name():
    lineage_table = _lineage_table_from_name(
        table_name="test_table", schema="default_schema", catalog="default_catalog"
    )
    assert lineage_table.catalog == "default_catalog"
    assert lineage_table.schema == "default_schema"
    assert lineage_table.table == "test_table"


def test_lineage_table_from_name_and_schema():
    lineage_table = _lineage_table_from_name(
        table_name="test_schema.test_table",
        schema="default_schema",
        catalog="default_catalog",
    )
    assert lineage_table.catalog == "default_catalog"
    assert lineage_table.schema == "test_schema"
    assert lineage_table.table == "test_table"


def test_lineage_table_from_name_and_schema_and_catalog():
    lineage_table = _lineage_table_from_name(
        table_name="test_catalog.test_schema.test_table",
        schema="default_schema",
        catalog="default_catalog",
    )
    assert lineage_table.catalog == "test_catalog"
    assert lineage_table.schema == "test_schema"
    assert lineage_table.table == "test_table"


def test_get_lineage_table_from_plan():
    table_dict = json.loads(
        """
    {
    "catalog": "test_catalog",
    "schemaTable": {
        "schema": "test_schema",
        "table": "test_table"
        }
    }
    """
    )
    lineage_table = _get_lineage_table_from_plan(table_dict)
    assert lineage_table.catalog == "test_catalog"
    assert lineage_table.schema == "test_schema"
    assert lineage_table.table == "test_table"


def test_get_input_tables_from_explain():
    explain_io_json = """
    {
      "inputTableColumnInfos" : [ {
        "table" : {
          "catalog" : "hive",
          "schemaTable" : {
            "schema" : "history",
            "table" : "palexiev2"
          }
        },
        "columnConstraints" : [ ],
        "estimate" : {
          "outputRowCount" : 0.0,
          "outputSizeInBytes" : 0.0,
          "cpuCost" : 0.0,
          "maxMemory" : 0.0,
          "networkCost" : 0.0
        }
      }, {
        "table" : {
          "catalog" : "hive",
          "schemaTable" : {
            "schema" : "history",
            "table" : "palexiev"
          }
        },
        "columnConstraints" : [ ],
        "estimate" : {
          "outputRowCount" : 0.0,
          "outputSizeInBytes" : 0.0,
          "cpuCost" : 0.0,
          "maxMemory" : 0.0,
          "networkCost" : 0.0
        }
      } ],
      "estimate" : {
        "outputRowCount" : 0.0,
        "outputSizeInBytes" : 0.0,
        "cpuCost" : 0.0,
        "maxMemory" : 0.0,
        "networkCost" : 0.0
      }
    }
    """
    explain_dict = json.loads(explain_io_json)
    lineage_tables = _get_input_tables_from_explain(
        explain_dict["inputTableColumnInfos"]
    )

    table1 = lineage_tables[0]
    assert table1.catalog == "hive"
    assert table1.schema == "history"
    assert table1.table == "palexiev2"

    table2 = lineage_tables[1]
    assert table2.catalog == "hive"
    assert table2.schema == "history"
    assert table2.table == "palexiev"


def test_get_rename_table_lineage_from_query():
    query = "alter table tbl_from rename to tbl_to"
    lineage_data = get_rename_table_lineage_from_query(
        query, "test_schema", "test_catalog"
    )
    assert lineage_data is not None
    assert lineage_data.query == query
    assert lineage_data.query_type == "rename_table"
    assert lineage_data.query_status == "OK"
    assert lineage_data.input_tables is not None
    assert len(lineage_data.input_tables) == 1
    assert lineage_data.input_tables[0].table == "tbl_from"
    assert lineage_data.input_tables[0].schema == "test_schema"
    assert lineage_data.input_tables[0].catalog == "test_catalog"
    assert lineage_data.output_table is not None
    assert lineage_data.output_table.table == "tbl_to"
    assert lineage_data.output_table.schema == "test_schema"
    assert lineage_data.output_table.catalog == "test_catalog"


def test_get_rename_table_lineage_from_query_with_schema():
    query = "alter table test_schema.tbl_from rename to test_schema.tbl_to"
    lineage_data = get_rename_table_lineage_from_query(
        query, "wrong_schema", "test_catalog"
    )
    assert lineage_data is not None
    assert lineage_data.query == query
    assert lineage_data.query_type == "rename_table"
    assert lineage_data.query_status == "OK"
    assert lineage_data.input_tables is not None
    assert len(lineage_data.input_tables) == 1
    assert lineage_data.input_tables[0].table == "tbl_from"
    assert lineage_data.input_tables[0].schema == "test_schema"
    assert lineage_data.input_tables[0].catalog == "test_catalog"
    assert lineage_data.output_table is not None
    assert lineage_data.output_table.table == "tbl_to"
    assert lineage_data.output_table.schema == "test_schema"
    assert lineage_data.output_table.catalog == "test_catalog"


def test_get_rename_table_lineage_from_query_full_names():
    query = "alter table test_catalog.test_schema.tbl_from rename to test_catalog.test_schema.tbl_to"
    lineage_data = get_rename_table_lineage_from_query(
        query, "wrong_schema", "wrong_catalog"
    )
    assert lineage_data is not None
    assert lineage_data.query == query
    assert lineage_data.query_type == "rename_table"
    assert lineage_data.query_status == "OK"
    assert lineage_data.input_tables is not None
    assert len(lineage_data.input_tables) == 1
    assert lineage_data.input_tables[0].table == "tbl_from"
    assert lineage_data.input_tables[0].schema == "test_schema"
    assert lineage_data.input_tables[0].catalog == "test_catalog"
    assert lineage_data.output_table is not None
    assert lineage_data.output_table.table == "tbl_to"
    assert lineage_data.output_table.schema == "test_schema"
    assert lineage_data.output_table.catalog == "test_catalog"


def test_get_rename_table_lineage_from_query_false_cases():
    assert (
        get_rename_table_lineage_from_query(
            "alter table tbl1 add column col1 int", "test_schema", "test_catalog"
        )
        is None
    )
    assert (
        get_rename_table_lineage_from_query(
            "alter table tbl1 rename column col1 to col2",
            "test_schema",
            "test_catalog",
        )
        is None
    )
    assert (
        get_rename_table_lineage_from_query(
            "alter view view1 rename to view2", "test_schema", "test_catalog"
        )
        is None
    )
