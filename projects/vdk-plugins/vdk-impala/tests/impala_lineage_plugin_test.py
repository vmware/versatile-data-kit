# Copyright 2021-2023 VMware, Inc.
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

    def test_does_query_have_lineage(self):
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage("SELECT * FROM table")
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "WITH temporaryTable(avgVal) as"
                "(SELECT avg(Salary)"
                "from Employee)"
                "SELECT EmployeeID,Name, Salary"
                "FROM Employee, temporaryTable"
                "WHERE Employee.Salary > temporaryTable.avgVal;"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "-- job_name: a-job\n-- op_id: an-op\nINSERT "
                "INTO TABLE schema.table  /* +SHUFFLE */\n "
                "SELECT t1.* FROM schema.table"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "-- job_name: a-job\n"
                "-- /* +SHUFFLE */ below is a query hint to "
                "Impala. Do not remove!\n "
                "INSERT OVERWRITE TABLE schema.table  /* +SHUFFLE */"
                "SELECT * FROM schema.table2;"
            )
        )

        self.assertFalse(ImpalaLineagePlugin._does_query_have_lineage("USE database;"))
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage("DROP TABLE table;")
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "select 1 -- testing if connection is alive."
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "alter table d2.mobile rename to d3.mobile;"
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "-- job_name: a-job\n"
                "-- op_id: an-op\n"
                "select 1 -- Testing if connection is alive."
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "-- job_name: a-job\n" "-- op_id: an-op\n" " DESCRIBE schema.table"
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "-- job_name: a-job\n" "-- op_id: an-op\n" " REFRESH schema.table"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "CREATE TABLE database_one.table_for_prod "
                "STORED AS PARQUET AS SELECT * FROM  database_two.table_for_prod;"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "CREATE TABLE database_one.table_for_prod "
                "STORED AS PARQUET AS SELECT\n"
                "* FROM  database_two.table_for_prod;"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "CREATE TABLE database_one.table_for_prod "
                "STORED AS PARQUET AS"
                "WITH temporaryTable(avgVal) as"
                "(SELECT avg(Salary)"
                "from Employee)"
                "SELECT EmployeeID,Name, Salary"
                "FROM Employee, temporaryTable"
                "WHERE Employee.Salary > temporaryTable.avgVal;"
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "CREATE TABLE database_one.table_for_prod " "STORED AS PARQUET"
            )
        )
        self.assertFalse(
            ImpalaLineagePlugin._does_query_have_lineage(
                "\n"
                "-- job_name: job-name\n"
                "-- op_id: job-name-1665673200-v9nth\n"
                "-- template: template-complex-name\n"
                "COMPUTE STATS shop1.users;\n"
            )
        )

        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "\n"
                "/***\n"
                "show create table database.incident;\n"
                "\n"
                "-- drop table if exists database.incident;\n"
                "\n"
                "-- invalidate metadata database.incident;\n"
                "\n"
                "CREATE TABLE database.incident\n"
                "(\n"
                "  id STRING,\n"
                "  incident STRING,\n"
                ")\n"
                "STORED AS PARQUET\n"
                "-- LOCATION check parquet files\n"
                ";\n"
                "***/\n"
                "\n"
                "with\n"
                "---------------------\n"
                "indent_tabs_enums\n"
                "---------------------\n"
                "as\n"
                "(\n"
                "  with\n"
                "  -------------------------\n"
                "  indent_tabs\n"
                "  -------------------------\n"
                "  as\n"
                "  (\n"
                "    select distinct trim( regexp_extract( reason, '\\d+', 0 )) issuenum\n"
                "    from   database.tasks\n"
                "    where  resource_type               in ('bundle' )\n"
                "    and    start_time                  >= '2020-06-01'\n"
                "    and    lower( trim( task_status )) in ( 'finished', 'succeeded' )\n"
                "    and    user_name                   =  'auto' \n"
                "  )\n"
                ")\n"
                "select    issue.id\n"
                "where     issue.id > '2019-02-01'\n"
                "                "
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "\n"
                "-- job_name: just-a-job\n"
                "-- op_id: just-a-job-1665673200-crhqw\n"
                "-- template: vdk.templates.load.dimension\n"
                "/* TO DO DROP AND RECREATE TARGET TABLE ON FULL RELOAD OR DATA TYPE CHANGE */\n"
                "\n"
                "-- DROP TABLE database_staging.a_table;\n"
                "-- CREATE TABLE database_staging.a_table  STORED AS PARQUET \n"
                "--    AS SELECT * FROM  database_production.a_table;\n"
                "\n"
                "-- /* +SHUFFLE */ below is a query hint to Impala. Do not remove!\n"
                "-- See https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_hints.html for details.\n"
                "INSERT OVERWRITE TABLE database_staging.a_table  /* +SHUFFLE */\n"
                "SELECT * FROM database_production.a_table;\n"
            )
        )
        self.assertTrue(
            ImpalaLineagePlugin._does_query_have_lineage(
                "\n"
                "/***\n"
                "show create table database_one.table_incidents;\n"
                "\n"
                "-- drop table if exists database_one.table_incidents;\n"
                "\n"
                "CREATE TABLE database_one.table_incidents\n"
                "(\n"
                "  id             STRING,\n"
                "  component      STRING,\n"
                "  category_group STRING,\n"
                "  category       STRING\n"
                ")\n"
                "STORED AS PARQUET\n"
                ";\n"
                "\n"
                "***/\n"
                "\n"
                "---------------------------------------------------\n"
                "insert overwrite table database_one.table_incidents\n"
                "---------------------------------------------------\n"
                "(\n"
                "  id,\n"
                "  component,\n"
                "  category_group,\n"
                "  category\n"
                ")\n"
                "select  isc.id\n"
                ",       isc.component\n"
                ",       'cat_group' category_group\n"
                ",       cfo.customvalue    category\n"
                "from    database_one.table_components isc\n"
                "join    database_two.value cfv on  isc.id = cfv.issue\n"
                "join    database_two.option cfo on cfv.f1 = cfo.f2\n"
                "   and cfv.stringvalue = cfo.id    \n"
                "where isc.component_group = 'Components' -- (6 of 12)\n"
            )
        )

    def test_parsing_query_profile(self):
        inputs = {"database_a.table1", "database_b.table2"}
        output = "database_c.table1"
        result = ImpalaLineagePlugin._parse_inputs_outputs(
            """
            00:SCAN HDFS [database_a.table1, RANDOM]
            01:SCAN HDFS [database_b.table2 w, RANDOM]
            03: WRITE TO HDFS [database_c.table1, OVERWRITE=true]
            """
        )
        self.assertEqual(set(result[0]), inputs)
        self.assertEqual(result[1], output)


if __name__ == "__main__":
    unittest.main()
