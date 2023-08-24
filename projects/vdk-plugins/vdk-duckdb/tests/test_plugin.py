# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest

import duckdb
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.duckdb.duckdb_configuration import DuckDBConfiguration
from vdk.plugin.duckdb.ingest_to_duckdb import IngestToDuckDB


class TestIngestToDuckDB(unittest.TestCase):
    def setUp(self):
        self.temp_db_file = "test_db.duckdb"
        self.connection = duckdb.connect(self.temp_db_file)

        duckdb_conf = Configuration(
            {
                "DUCKDB_FILE": self.temp_db_file,
                "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": False,  # Changed configuration to False
            },
            {},
        )
        self.conf = DuckDBConfiguration(duckdb_conf)
        self.ingester = IngestToDuckDB(self.conf)

    def tearDown(self):
        self.connection.close()
        os.remove(self.temp_db_file)

    def test_ingest_payload(self):
        destination_table = "test_table"
        payload = [{"col1": 1, "col2": "text"}]

        try:
            self.ingester.ingest_payload(payload, destination_table=destination_table)
        except UserCodeError as e:
            self.assertIn(
                "destination_table does not exist in the target database", str(e)
            )

        # Check the table contents if the ingest didn't raise an error
        else:
            with duckdb.connect(self.temp_db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {destination_table}")
                result = cursor.fetchall()
                self.assertEqual(result, [(1, "text")])

    if __name__ == "__main__":
        unittest.main()
