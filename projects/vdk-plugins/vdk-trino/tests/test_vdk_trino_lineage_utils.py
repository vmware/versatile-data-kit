# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import unittest

from vdk.plugin.trino.lineage_utils import _get_input_tables_from_explain
from vdk.plugin.trino.lineage_utils import _get_lineage_table_from_plan
from vdk.plugin.trino.lineage_utils import _lineage_table_from_name
from vdk.plugin.trino.lineage_utils import is_heartbeat_query


class TestStringMethods(unittest.TestCase):
    def test_is_heartbeat_query(self):
        assert is_heartbeat_query("select 1")
        assert is_heartbeat_query("select 'aaa'")
        assert not is_heartbeat_query("select * from a_table")

    def test_lineage_table_from_name(self):
        lineage_table = _lineage_table_from_name(
            table_name="test_table", schema="default_schema", catalog="default_catalog"
        )
        assert lineage_table.catalog == "default_catalog"
        assert lineage_table.schema == "default_schema"
        assert lineage_table.table == "test_table"

    def test_lineage_table_from_name_and_schema(self):
        lineage_table = _lineage_table_from_name(
            table_name="test_schema.test_table",
            schema="default_schema",
            catalog="default_catalog",
        )
        assert lineage_table.catalog == "default_catalog"
        assert lineage_table.schema == "test_schema"
        assert lineage_table.table == "test_table"

    def test_lineage_table_from_name_and_schema_and_catalog(self):
        lineage_table = _lineage_table_from_name(
            table_name="test_catalog.test_schema.test_table",
            schema="default_schema",
            catalog="default_catalog",
        )
        assert lineage_table.catalog == "test_catalog"
        assert lineage_table.schema == "test_schema"
        assert lineage_table.table == "test_table"

    def test_get_lineage_table_from_plan(self):
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

    def test_get_input_tables_from_explain(self):
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


if __name__ == "__main__":
    unittest.main()
