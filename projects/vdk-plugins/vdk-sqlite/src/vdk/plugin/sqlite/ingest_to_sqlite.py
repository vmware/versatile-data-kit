# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import collections
import logging
import pathlib
from contextlib import closing
from sqlite3 import Cursor
from sqlite3.dbapi2 import ProgrammingError
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
from vdk.plugin.sqlite.sqlite_connection import SQLiteConnection

log = logging.getLogger(__name__)


class IngestToSQLite(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a SQLite database
    """

    def __init__(self, conf: SQLiteConfiguration):
        self.conf = conf

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

        :param payload:
            the payload to be ingested
        :param destination_table:
            the name of the table receiving the payload in the target database
        :param target:
            the path to the database file; if left None, defaults to
            VDK_INGEST_TARGET_DEFAULT
        :param collection_id:
            an identifier specifying that data from different method
            invocations belongs to the same collection
        :param metadata:
            an IngestionMetadata object that contains metadata about the
            pre-ingestion and ingestion operations
        """
        target = target or self.conf.get_sqlite_file()
        if not target:
            errors.report_and_throw(
                UserCodeError(
                    "Failed to proceed with ingestion",
                    "Target was not supplied as a parameter",
                    "Will not proceed with ingestion",
                    "Set target either through the target parameter in send_object_for_ingestion,"
                    "or through either of the VDK_INGEST_TARGET_DEFAULT or VDK_SQLITE_FILE environment variables",
                )
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

        with SQLiteConnection(pathlib.Path(target)).new_connection() as conn:
            with closing(conn.cursor()) as cur:
                if self.conf.get_auto_create_table_enabled():
                    self.__create_table_if_not_exists(cur, destination_table, payload)
                else:
                    self.__check_destination_table_exists(destination_table, cur)
                self.__ingest_payload(destination_table, payload, cur)

    def __ingest_payload(
        self, destination_table: str, payload: List[dict], cur: Cursor
    ) -> None:
        values, query = self.__create_query(destination_table, payload, cur)
        for obj in values:
            try:
                cur.execute(query, obj)
                log.debug("Payload was ingested.")
            except Exception as e:
                if isinstance(e, ProgrammingError):
                    log.warning(
                        "Failed to sent payload. An issue with the SQL query occurred."
                    )
                    errors.report(ResolvableBy.USER_ERROR, e)
                else:
                    errors.report(errors.ResolvableBy.PLATFORM_ERROR, e)
                raise e

    def __check_destination_table_exists(
        self, destination_table: str, cur: Cursor
    ) -> None:
        columns = self.__table_columns(cur, destination_table)
        if not columns:  # check table with no columns does not exists
            errors.report_and_throw(
                UserCodeError(
                    "Cannot send payload for ingestion to SQLite database.",
                    "destination_table does not exist in the target database.",
                    "Will not be able to send the payloads and will throw exception."
                    "Likely the job would fail",
                    "Make sure the destination_table exists in the target SQLite database.",
                )
            )

    def __table_columns(
        self, cur: Cursor, destination_table: str
    ) -> List[Tuple[str, str]]:
        """
        :param cur: database cursor
        :param destination_table: the table name queried
        :return: return a list of tuples in format: [(column_name, column_type), ...]
        """
        # https://tableplus.com/blog/2018/04/sqlite-check-whether-a-table-exists.html
        columns = []
        for row in cur.execute(
            f"select name, type from PRAGMA_TABLE_INFO('{destination_table}');"
        ):
            columns.append((row[0], row[1]))
        return columns

    def __create_query(
        self, destination_table: str, payload: List[dict], cur: Cursor
    ) -> Tuple[list, str]:
        fields = [
            field_tuple[0]
            for field_tuple in cur.execute(
                f"SELECT name FROM PRAGMA_TABLE_INFO('{destination_table}')"
            ).fetchall()
        ]

        # verify that the payload header and table column names match
        for obj in payload:
            if collections.Counter(fields) != collections.Counter(obj.keys()):
                errors.report_and_throw(
                    UserCodeError(
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
                )

        # the query fstring evaluates to 'INSERT INTO dest_table (val1, val2, val3) VALUES (?, ?, ?)'
        # assuming dest_table is the destination_table and val1, val2, val3 are the fields of that table
        values = [[obj.get(field) for field in fields] for obj in payload]
        fields = [field if " " not in field else f'"{field}"' for field in fields]
        query = f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES ({', '.join(['?' for _ in fields])})"
        return values, query

    def __create_table_if_not_exists(
        self, cur: Cursor, destination_table: str, payload: List[dict]
    ):
        columns = self.__table_columns(cur, destination_table)
        if not columns:
            log.info(
                f"Table {destination_table} does not exists. "
                f"Will auto-create it now based on first batch of input data."
            )
            columns = self.__infer_columns_from_payload(payload)
            self.__create_table(cur, destination_table, columns)
            log.info(f"Table {destination_table} created.")

    @staticmethod
    def __create_table(cur: Cursor, destination_table: str, columns: Dict[str, str]):
        """
        Creates table from given list of columns and table name
        """
        names = [
            f"{col_name} {col_type}"
            if " " not in col_name
            else f'"{col_name}" {col_type}'
            for col_name, col_type in columns.items()
        ]
        columns_as_sql_expression = ",".join(names)
        sql = f"CREATE TABLE IF NOT EXISTS {destination_table} ( {columns_as_sql_expression} );"
        log.debug(f"Create table using {sql}")
        cur.execute(sql)

    def __infer_columns_from_payload(self, payload: List[Dict]):
        """
        Infer the columns from payload. It will infer by getting all the keys from every row.
        So even if row have different number of keys it would find all the columns.
        The type is inferred based on the first non-None value
        :param payload: the payload
        :return: dictionary with key being column name and value the type: dict[column_name, column_type]
        """
        columns = dict()
        for row in payload:
            for col, val in row.items():
                if col not in columns:
                    columns[col] = self.__python_value_to_sqlite_type(val)
                elif columns[col] == "NULL":
                    columns[col] = self.__python_value_to_sqlite_type(val)
        # if there's column with NULL only, set type to TEXT.
        columns = {
            col: typ if typ != "NULL" else "TEXT" for col, typ in columns.items()
        }
        return columns

    @staticmethod
    def __python_value_to_sqlite_type(value: Any):
        # https://www.sqlite.org/datatype3.html
        value_type = type(value)
        if value_type == bool or value_type == int:
            return "INTEGER"
        if value_type == bytes:
            return "BLOB"
        if value_type == float:
            return "REAL"
        if value_type == type(None):
            return "NULL"
        else:
            return "TEXT"
