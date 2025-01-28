# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from contextlib import closing
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import duckdb
from vdk.api.plugin.plugin_input import PEP249Connection
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.core import errors
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.duckdb.duckdb_configuration import DuckDBConfiguration

log = logging.getLogger(__name__)


class IngestToDuckDB(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a DuckDB database
    """

    def __init__(
        self,
        conf: DuckDBConfiguration,
        new_connection_func: Callable[[], PEP249Connection],
    ):
        self._new_connection_func = new_connection_func
        self._conf = conf

    def ingest_payload(
        self,
        payload: List[Dict[str, Any]],
        destination_table: Optional[str] = None,
        target: str = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> None:
        """
        Performs the ingestion
        """
        if not payload:
            log.debug(
                f"Payload is empty. "
                f"Nothing to ingest into {target}, table {destination_table} and collection_id: {collection_id}"
            )
            return

        log.info(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        with closing(self._new_connection_func().cursor()) as cur:
            if self._conf.get_auto_create_table_enabled():
                self.__create_table_if_not_exists(cur, destination_table, payload)
            else:
                self.__check_destination_table_exists(destination_table, cur)
            self.__ingest_payload(destination_table, payload, cur)

    def __ingest_payload(
        self, destination_table: str, payload: List[dict], cur: duckdb.cursor
    ) -> None:
        # Start a new transaction
        cur.execute("BEGIN TRANSACTION")

        try:
            keys = payload[0].keys()
            values = [[dic[k] for k in keys] for dic in payload]

            placeholders = ", ".join(["?" for _ in keys])
            sql = f"INSERT INTO {destination_table} ({', '.join(keys)}) VALUES ({placeholders})"

            cur.executemany(sql, values)

            cur.execute("COMMIT")
        except Exception:
            cur.execute("ROLLBACK")
            raise

    def __check_destination_table_exists(
        self, destination_table: str, cur: duckdb.cursor
    ) -> None:
        if not self._check_if_table_exists(destination_table, cur):
            errors.report_and_throw(
                UserCodeError(
                    "Cannot send payload for ingestion to DuckDB database.",
                    "destination_table does not exist in the target database.",
                    "Will not be able to send the payloads and will throw exception."
                    "Likely the job would fail",
                    "Make sure the destination_table exists in the target DuckDB database.",
                )
            )

    @staticmethod
    def _check_if_table_exists(table_name: str, cur: duckdb.cursor) -> bool:
        cur.execute("show tables")
        tables = cur.fetchall()
        return (table_name,) in tables

    def __table_columns(
        self, cur: duckdb.cursor, destination_table: str
    ) -> List[Tuple[str, str]]:
        columns = []
        if self._check_if_table_exists(destination_table, cur):
            cur.execute(
                f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{destination_table}'"
            )
            for row in cur.fetchall():
                columns.append((row[0], row[1]))
        return columns

    def __create_table_if_not_exists(
        self, cur: duckdb.cursor, destination_table: str, payload: List[dict]
    ):
        if not self._check_if_table_exists(destination_table, cur):
            log.info(
                f"Table {destination_table} does not exists. "
                f"Will auto-create it now based on first batch of input data."
            )
            columns = self.__infer_columns_from_payload(payload)
            self.__create_table(cur, destination_table, columns)
            log.info(f"Table {destination_table} created.")

    @staticmethod
    def __create_table(
        cur: duckdb.cursor, destination_table: str, columns: Dict[str, str]
    ):
        names = [
            f"{col_name} {col_type}"
            if " " not in col_name
            else f'"{col_name}" {col_type}'
            for col_name, col_type in columns.items()
        ]
        columns_as_sql_expression = ",".join(names)
        sql = f"CREATE TABLE IF NOT EXISTS {destination_table} ({columns_as_sql_expression})"
        log.debug(f"Create table using {sql}")
        cur.execute(sql)

    def __infer_columns_from_payload(self, payload: List[Dict]):
        columns = dict()
        for row in payload:
            for col, val in row.items():
                if col not in columns:
                    columns[col] = self.__python_value_to_duckdb_type(val)
                elif columns[col] == "NULL":
                    columns[col] = self.__python_value_to_duckdb_type(val)
        columns = {
            col: typ if typ != "NULL" else "VARCHAR" for col, typ in columns.items()
        }
        return columns

    @staticmethod
    def __python_value_to_duckdb_type(value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "FLOAT"
        if isinstance(value, bool):
            return "BOOLEAN"
        if isinstance(value, str):
            return "VARCHAR"
        return "VARCHAR"
