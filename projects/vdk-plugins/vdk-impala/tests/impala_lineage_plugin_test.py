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


if __name__ == "__main__":
    unittest.main()
