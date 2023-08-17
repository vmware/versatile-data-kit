import os
import unittest

import duckdb
from vdk.internal.core.config import Configuration
from vdk.plugin.duckdb.duckdb_configuration import DuckDBConfiguration
from vdk.plugin.duckdb.ingest_to_duckdb import IngestToDuckDB


class TestIngestToDuckDB(unittest.TestCase):

    def setUp(self):
        self.temp_db_file = "test_db.duckdb"

        self.connection = duckdb.connect(self.temp_db_file)
        cur = self.connection.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            col1 INTEGER,
            col2 TEXT
        )
        """)
        cur.close()

        duckdb_conf = Configuration({
            "DUCKDB_FILE": self.temp_db_file,
            "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": True
        }, {})
        self.conf = DuckDBConfiguration(duckdb_conf)
        self.ingester = IngestToDuckDB(self.conf)

    def tearDown(self):
        self.connection.close()
        os.remove(self.temp_db_file)

    def test_ingest_payload(self):
        destination_table = "test_table"
        payload = [{"col1": 1, "col2": "text"}]

        self.ingester.ingest_payload(payload, destination_table=destination_table)

        with duckdb.connect(self.temp_db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {destination_table}")
            result = cursor.fetchall()
            self.assertEqual(result, [(1, "text")])

    if __name__ == '__main__':
        unittest.main()

