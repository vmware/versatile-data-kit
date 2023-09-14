# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import logging
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin

log = logging.getLogger(__name__)


class IngestToOracle(IIngesterPlugin):
    def __init__(self, connections: ManagedConnectionRouter):
        self.conn = connections.open_connection("ORACLE").connect()
        self.cursor = self.conn.cursor()
        self.table_cache = set()  # Cache to store existing tables
        self.column_cache = {}  # New cache for columns

    @staticmethod
    def _get_oracle_type(value):
        type_mappings = {
            int: "NUMBER",
            float: "FLOAT",
            Decimal: "DECIMAL(14, 8)",
            str: "VARCHAR2(255)",
            datetime.datetime: "TIMESTAMP",
            bool: "NUMBER(1)",
            bytes: "BLOB",
        }
        return type_mappings.get(type(value), "VARCHAR2(255)")

    def _table_exists(self, table_name):
        if table_name.upper() in self.table_cache:
            return True

        self.cursor.execute(
            f"SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
            [table_name.upper()],
        )
        exists = bool(self.cursor.fetchone()[0])

        if exists:
            self.table_cache.add(table_name.upper())

        return exists

    def _create_table(self, table_name, payload):
        column_defs = [
            f"{col} {self._get_oracle_type(payload[col])}" for col in payload.keys()
        ]
        create_table_sql = (
            f"CREATE TABLE {table_name.upper()} ({', '.join(column_defs)})"
        )
        self.cursor.execute(create_table_sql)

    def _cache_columns(self, table_name):
        try:
            self.cursor.execute(
                f"SELECT column_name FROM user_tab_columns WHERE table_name = '{table_name.upper()}'"
            )
            result = self.cursor.fetchall()
            self.column_cache[table_name.upper()] = {column[0] for column in result}
        except Exception as e:
            log.error(
                "An exception occurred while trying to cache columns. Ignoring for now."
            )
            log.exception(e)

    def _add_columns(self, table_name, payload):
        if table_name.upper() not in self.column_cache:
            self._cache_columns(table_name)

        existing_columns = self.column_cache[table_name.upper()]

        # Find unique new columns from all rows in the payload
        all_columns = {col.upper() for row in payload for col in row.keys()}
        new_columns = all_columns - existing_columns

        if new_columns:
            column_defs = []
            for col in new_columns:
                sample_value = next(
                    (row[col] for row in payload if row.get(col) is not None), None
                )
                column_type = (
                    self._get_oracle_type(sample_value)
                    if sample_value is not None
                    else "VARCHAR2(255)"
                )
                column_defs.append(f"{col} {column_type}")

            alter_sql = (
                f"ALTER TABLE {table_name.upper()} ADD ({', '.join(column_defs)})"
            )
            self.cursor.execute(alter_sql)
            self.column_cache[table_name.upper()].update(new_columns)

    # TODO: Cast string to correct column type
    def _cast_to_correct_type(self, value):
        if type(value) is Decimal:
            return float(value)
        return value

    # TODO: Optimize this once tests are running in CI
    def _insert_data(self, table_name, payload):
        if not payload:
            return

        # group dicts by key set
        batches = {}
        for p in payload:
            batch = frozenset(p.keys())
            if batch not in batches:
                batches[batch] = []
            batches[batch].append(p)

        # create queries for groups of dicts with the same key set
        queries = []
        batch_data = []
        for column_names, batch in batches.items():
            columns = list(column_names)
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':' + str(i + 1) for i in range(len(columns))])})"
            queries.append(insert_sql)
            temp_data = []
            for row in batch:
                temp = [self._cast_to_correct_type(row[col]) for col in columns]
                temp_data.append(temp)
            batch_data.append(temp_data)

        # batch execute queries for dicts with the same key set
        for i in range(len(queries)):
            self.cursor.executemany(queries[i], batch_data[i])

    def ingest_payload(
        self,
        payload: List[Dict[str, Any]],
        destination_table: Optional[str] = None,
        target: str = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> None:
        if not payload:
            return None
        if not destination_table:
            raise ValueError("Destination table must be specified if not in payload.")

        if not self._table_exists(destination_table):
            self._create_table(destination_table, payload[0])
            self._cache_columns(destination_table)

        self._add_columns(destination_table, payload)
        self._insert_data(destination_table, payload)

        self.conn.commit()
        return metadata
