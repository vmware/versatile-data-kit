# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest

from vdk.api.lineage.model.sql.model import LineageTable
from vdk.plugin.impala.impala_lineage_plugin import ImpalaLineagePlugin


class ImpalaLineagePluginTest(unittest.TestCase):
    def test_get_lineage_table_from_table_name_valid_name(self):
        actual = ImpalaLineagePlugin._get_lineage_table_from_table_name("schema.table")
        expected = LineageTable(schema="schema", table="table", catalog=None)
        self.assertEqual(expected, actual)

    def test_get_lineage_table_from_table_name_none(self):
        self.assertIsNone(ImpalaLineagePlugin._get_lineage_table_from_table_name(None))

    def test_is_query_have_lineage(self):
        self.assertTrue(ImpalaLineagePlugin._is_query_have_lineage("SELECT * FROM table"))
        self.assertTrue(ImpalaLineagePlugin._is_query_have_lineage("WITH temporaryTable(avgVal) as"
                                                                   "(SELECT avg(Salary)"
                                                                   "from Employee)"
                                                                   "SELECT EmployeeID,Name, Salary"
                                                                   "FROM Employee, temporaryTable"
                                                                   "WHERE Employee.Salary > temporaryTable.avgVal;"))
        self.assertTrue(ImpalaLineagePlugin._is_query_have_lineage("-- job_name: a-job\n-- op_id: an-op\nINSERT "
                                                                   "INTO TABLE schema.table  /* +SHUFFLE */\n "
                                                                   "SELECT t1.* FROM schema.table"))
        self.assertTrue(ImpalaLineagePlugin._is_query_have_lineage("-- job_name: a-job\n"
                                                                   "-- /* +SHUFFLE */ below is a query hint to "
                                                                   "Impala. Do not remove!\n "
                                                                   "INSERT OVERWRITE TABLE schema.table  /* +SHUFFLE */"
                                                                   "SELECT * FROM schema.table2;"))

        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("USE database;"))
        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("DROP TABLE table;"))
        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("select 1 -- testing if connection is alive."))
        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("alter table d2.mobile rename to d3.mobile;"))
        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("-- job_name: a-job\n"
                                                                    "-- op_id: an-op\n"
                                                                    "select 1 -- Testing if connection is alive."))
        self.assertFalse(ImpalaLineagePlugin._is_query_have_lineage("-- job_name: a-job\n"
                                                                    "-- op_id: an-op\n"
                                                                    "DESCRIBE schema.table"))


if __name__ == "__main__":
    unittest.main()
