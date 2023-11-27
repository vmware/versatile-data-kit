# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import logging
import math
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from vdk.api.plugin.plugin_input import PEP249Connection
from vdk.internal.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from vdk.internal.builtin_plugins.connection.managed_cursor import ManagedCursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin

log = logging.getLogger(__name__)


class IngestToOracle(IIngesterPlugin):
    def __init__(self, connections: ManagedConnectionRouter):
        self.conn: PEP249Connection = connections.open_connection("ORACLE").connect()
        self.cursor: ManagedCursor = self.conn.cursor()
        self.table_cache: Set[str] = set()  # Cache to store existing tables
        self.column_cache: Dict[str, Dict[str, str]] = {}  # New cache for columns

    @staticmethod
    def _get_oracle_type(value: Any) -> str:
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

    def _table_exists(self, table_name: str) -> bool:
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

    def _create_table(self, table_name: str, row: Dict[str, Any]) -> None:
        column_defs = [f"{col} {self._get_oracle_type(row[col])}" for col in row.keys()]
        create_table_sql = (
            f"CREATE TABLE {table_name.upper()} ({', '.join(column_defs)})"
        )
        self.cursor.execute(create_table_sql)

    def _cache_columns(self, table_name: str) -> None:
        try:
            self.cursor.execute(
                f"SELECT column_name, data_type, data_scale FROM user_tab_columns WHERE table_name = '{table_name.upper()}'"
            )
            result = self.cursor.fetchall()
            self.column_cache[table_name.upper()] = {
                col: ("DECIMAL" if data_type == "NUMBER" and data_scale else data_type)
                for (col, data_type, data_scale) in result
            }
        except Exception as e:
            # TODO: https://github.com/vmware/versatile-data-kit/issues/2932
            log.error(
                "An exception occurred while trying to cache columns. Ignoring for now."
            )
            log.exception(e)

    def _add_columns(self, table_name: str, payload: List[Dict[str, Any]]) -> None:
        if table_name.upper() not in self.column_cache:
            self._cache_columns(table_name)

        existing_columns = self.column_cache[table_name.upper()]

        # Find unique new columns from all rows in the payload
        all_columns = {col.upper() for row in payload for col in row.keys()}
        new_columns = all_columns - existing_columns.keys()
        column_defs = []
        if new_columns:
            for col in new_columns:
                sample_value = next(
                    (row[col] for row in payload if row.get(col) is not None), None
                )
                column_type = (
                    self._get_oracle_type(sample_value)
                    if sample_value is not None
                    else "VARCHAR2(255)"
                )
                column_defs.append((col, column_type))

            string_defs = [f"{col_def[0]} {col_def[1]}" for col_def in column_defs]
            alter_sql = (
                f"ALTER TABLE {table_name.upper()} ADD ({', '.join(string_defs)})"
            )
            self.cursor.execute(alter_sql)
            self.column_cache[table_name.upper()].update(column_defs)

    # TODO: https://github.com/vmware/versatile-data-kit/issues/2929
    # TODO: https://github.com/vmware/versatile-data-kit/issues/2930
    def _cast_to_correct_type(self, table: str, column: str, value: Any) -> Any:
        def cast_string_to_type(db_type: str, payload_value: str) -> Any:
            if db_type == "FLOAT" or db_type == "DECIMAL":
                return float(payload_value)
            if db_type == "NUMBER":
                payload_value = payload_value.capitalize()
                return (
                    bool(payload_value)
                    if payload_value in ["True", "False"]
                    else int(payload_value)
                )
            if "TIMESTAMP" in db_type:
                return datetime.datetime.strptime(payload_value, "%Y-%m-%dT%H:%M:%S")
            if db_type == "BLOB":
                return payload_value.encode("utf-8")
            return payload_value

        if (isinstance(value, float) or isinstance(value, int)) and math.isnan(value):
            return None
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            col_type = self.column_cache.get(table.upper()).get(column.upper())
            return cast_string_to_type(col_type, value)
        return value

    # TODO: Look into potential optimizations
    # TODO: https://github.com/vmware/versatile-data-kit/issues/2931
    def _insert_data(self, table_name: str, payload: List[Dict[str, Any]]) -> None:
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
                temp = [
                    self._cast_to_correct_type(table_name, col, row[col])
                    for col in columns
                ]
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

        # TODO: test if we need this commit statement (most probably we don't, the connection already commits after every transaction)
        self.conn.commit()
        return metadata
