import collections
import logging
from contextlib import closing

import duckdb
from duckdb import DuckDBPyConnection, DuckDBPyCursor
from typing import Any, Dict, List, Optional, Tuple

from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.core import errors
from vdk.plugin.duckdb.duckdb_configuration import DuckDBConfiguration
from vdk.plugin.duckdb.duckdb_connection import DuckDBConnection

log = logging.getLogger(__name__)


class IngestToDuckDB(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a DuckDB database
    """

    def __init__(self, conf: DuckDBConfiguration):
        self.conf = conf

    def create_table(test_table: str, cur: DuckDBPyCursor):
        cur.execute(f"CREATE TABLE{test_table} (col1 INT, col2 TEXT)")

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
        target = target or self.conf.get_duckdb_file()
        if not target:
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                "Failed to proceed with ingestion",
                "Target was not supplied as a parameter",
                "Will not proceed with ingestion",
                (
                    "Set target either through the target parameter in send_object_for_ingestion,"
                    "or through either of the VDK_INGEST_TARGET_DEFAULT or VDK_DUCKDB_FILE environment variables"
                ),
            )
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

        with DuckDBConnection(duckdb_file=target).new_connection() as conn:
            with closing(conn.cursor()) as cur:
                if self.conf.get_auto_create_table_enabled():
                    self.__create_table_if_not_exists(cur, destination_table, payload)
                else:
                    self.__check_destination_table_exists(destination_table, cur)
                self.__ingest_payload(destination_table, payload, cur)

    def __ingest_payload(
            self, destination_table: str, payload: List[dict], cur: duckdb.cursor
    ) -> None:
        values, query = self.__create_query(destination_table, payload, cur)
        for obj in values:
            try:
                cur.execute(query, obj)
                log.debug("Payload was ingested.")
            except Exception as e:
                errors.log_and_rethrow(
                    errors.ResolvableBy.PLATFORM_ERROR,
                    log,
                    "Failed to sent payload",
                    "Unknown error. Error message was : " + str(e),
                    "Will not be able to send the payload for ingestion",
                    "See error message for help ",
                    e,
                    wrap_in_vdk_error=True,
                    )

    def __check_destination_table_exists(
            self, destination_table: str, cur: DuckDBPyCursor
    ) -> None:
        if not self._check_if_table_exists(destination_table, cur):
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                "Cannot send payload for ingestion to DuckDB database.",
                "destination_table does not exist in the target database.",
                "Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                "Make sure the destination_table exists in the target DuckDB database.",
            )

    @staticmethod
    def _check_if_table_exists(table_name: str, cur: duckdb.cursor) -> bool:
        cur.execute('show tables')
        tables = cur.fetchall()
        return (table_name, ) in tables

    def __table_columns(
            self, cur: DuckDBPyCursor, destination_table: str
    ) -> List[Tuple[str, str]]:
        columns = []
        if self._check_if_table_exists(destination_table, cur):
            for row in cur.execute(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{destination_table}'"
            ).fetchall():
                columns.append((row[0], row[1]))
        return columns

    def __create_query(
            self, destination_table: str, payload: List[dict], cur: DuckDBPyCursor
    ) -> Tuple[list, str]:
        fields = [
            field_tuple[0]
            for field_tuple in cur.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{destination_table}'"
            ).fetchall()
        ]

        for obj in payload:
            if collections.Counter(fields) != collections.Counter(obj.keys()):
                errors.log_and_throw(
                    errors.ResolvableBy.USER_ERROR,
                    log,
                    "Failed to sent payload",
                    f"""
                    One or more column names in the input data did NOT
                    match corresponding column names in the database.
                       Input Table Columns: {list(obj.keys())}
                    Database Table Columns: {fields}
                    """,
                    "Will not be able to send the payload for ingestion",
                    "See error message for help ",
                )

        values = [[obj.get(field) for field in fields] for obj in payload]
        fields = [field if " " not in field else f'"{field}"' for field in fields]
        query = f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES ({', '.join(['?' for _ in fields])})"
        return values, query

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
    def __create_table(cur: DuckDBPyCursor, destination_table: str, columns: Dict[str, str]):
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
