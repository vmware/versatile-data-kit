# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
import logging
import math
import re
from decimal import Decimal
from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from vdk.api.plugin.plugin_input import PEP249Connection
from vdk.internal.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from vdk.internal.builtin_plugins.connection.managed_cursor import ManagedCursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin

log = logging.getLogger(__name__)


# Functions for escaping special characters
def _is_plain_identifier(identifier: str) -> bool:
    # https://docs.oracle.com/en/error-help/db/ora-00904/
    # Alphanumeric that doesn't start with a number
    # Can contain and start with $, # and _
    regex = "^[A-Za-z\\$#_][0-9A-Za-z\\$#_]*$"
    return bool(re.fullmatch(regex, identifier))


def _normalize_identifier(identifier: str) -> str:
    return identifier.upper() if _is_plain_identifier(identifier) else identifier


def _escape_special_chars(value: str) -> str:
    return value if _is_plain_identifier(value) else f'"{value}"'


class TableCache:
    def __init__(self, cursor: ManagedCursor):
        self._tables: Dict[str, Dict[str, str]] = {}
        self._cursor = cursor

    def cache_columns(self, table: str) -> None:
        # exit if the table columns have already been cached
        if table.upper() in self._tables and self._tables[table.upper()]:
            return
        try:
            self._cursor.execute(
                f"SELECT column_name, data_type, data_scale FROM user_tab_columns WHERE table_name = '{table.upper()}'"
            )
            result = self._cursor.fetchall()
            self._tables[table.upper()] = {
                col: ("DECIMAL" if data_type == "NUMBER" and data_scale else data_type)
                for (col, data_type, data_scale) in result
            }
        except Exception as e:
            # TODO: https://github.com/vmware/versatile-data-kit/issues/2932
            log.exception(
                "An error occurred while trying to cache columns. Ignoring for now.", e
            )

    def get_columns(self, table: str) -> Dict[str, str]:
        return self._tables[table.upper()]

    def update_from_col_defs(self, table: str, col_defs) -> None:
        self._tables[table.upper()].update(col_defs)

    def get_col_type(self, table: str, col: str) -> str:
        return self._tables.get(table.upper()).get(
            col.upper() if _is_plain_identifier(col) else col
        )

    def table_exists(self, table: str) -> bool:
        if table.upper() in self._tables:
            return True

        self._cursor.execute(
            f"SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
            [table.upper()],
        )
        exists = bool(self._cursor.fetchone()[0])

        if exists:
            self._tables[table.upper()] = {}

        return exists


class IngestToOracle(IIngesterPlugin):
    def __init__(self, connections: ManagedConnectionRouter):
        self.conn: PEP249Connection = connections.open_connection("ORACLE").connect()
        self.cursor: ManagedCursor = self.conn.cursor()
        self.table_cache: TableCache = TableCache(self.cursor)  # New cache for columns

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

    def _create_table(self, table_name: str, row: Dict[str, Any]) -> None:
        column_defs = [
            f"{_escape_special_chars(col)} {self._get_oracle_type(row[col])}"
            for col in row.keys()
        ]
        create_table_sql = (
            f"CREATE TABLE {table_name.upper()} ({', '.join(column_defs)})"
        )
        self.cursor.execute(create_table_sql)

    def _add_columns(self, table_name: str, payload: List[Dict[str, Any]]) -> None:
        self.table_cache.cache_columns(table_name)
        existing_columns = self.table_cache.get_columns(table_name)

        # Find unique new columns from all rows in the payload
        all_columns = {
            _normalize_identifier(col) for row in payload for col in row.keys()
        }
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

            string_defs = [
                f"{_escape_special_chars(col_def[0])} {col_def[1]}"
                for col_def in column_defs
            ]
            alter_sql = (
                f"ALTER TABLE {table_name.upper()} ADD ({', '.join(string_defs)})"
            )
            self.cursor.execute(alter_sql)
            self.table_cache.update_from_col_defs(table_name, column_defs)

    # TODO: https://github.com/vmware/versatile-data-kit/issues/2929
    # TODO: https://github.com/vmware/versatile-data-kit/issues/2930
    def _cast_to_correct_type(self, table: str, column: str, value: Any) -> Any:
        if isinstance(value, float) and math.isnan(value):
            return None

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
                try:
                    return datetime.datetime.strptime(
                        payload_value, "%Y-%m-%dT%H:%M:%S"
                    )
                except ValueError as v:
                    if len(v.args) > 0 and v.args[0].startswith(
                        "unconverted data remains:"
                    ):
                        return datetime.datetime.strptime(
                            payload_value, "%Y-%m-%dT%H:%M:%S.%f"
                        )
                    else:
                        raise
            if db_type == "BLOB":
                return payload_value.encode("utf-8")
            return payload_value

        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, str):
            col_type = self.table_cache.get_col_type(table, column)
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
            query_columns = [_escape_special_chars(col) for col in columns]
            insert_sql = f"INSERT INTO {table_name} ({', '.join(query_columns)}) VALUES ({', '.join([':' + str(i + 1) for i in range(len(query_columns))])})"
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

        if not self.table_cache.table_exists(destination_table):
            self._create_table(destination_table, payload[0])
            self.table_cache.cache_columns(destination_table)

        self._add_columns(destination_table, payload)
        self._insert_data(destination_table, payload)

        self.conn.commit()
        return metadata
