# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import collections
import logging
import pathlib
from contextlib import closing
from sqlite3 import Cursor
from sqlite3.dbapi2 import ProgrammingError
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.core import errors
from vdk.internal.sqlite_connection import SQLiteConfiguration
from vdk.internal.sqlite_connection import SQLiteConnection

log = logging.getLogger(__name__)


class IngestToSQLite(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a SQLite database
    """

    def __init__(self, conf: SQLiteConfiguration):
        self.conf = conf

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: str = None,
        collection_id: Optional[str] = None,
    ) -> None:
        """
        Performs the ingestion

        :param payload:
            the payload to be ingested
        :param destination_table:
            the name of the table receiving the payload in the target database
        :param target:
            the path to the database file; if left None, defaults to VDK_INGEST_TARGET_DEFAULT
        :param collection_id:
            an identifier specifying that data from different method invocations belongs to the same collection
        """
        target = target or self.conf.get_sqlite_file()
        if not target:
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                "Failed to proceed with ingestion",
                "Target was not supplied as a parameter",
                "Will not proceed with ingestion",
                (
                    "Set target either through the target parameter in send_object_for_ingestion,"
                    "or through either of the VDK_INGEST_TARGET_DEFAULT or VDK_SQLITE_FILE environment variables"
                ),
            )

        log.info(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        with SQLiteConnection(pathlib.Path(target)).new_connection() as conn:
            with closing(conn.cursor()) as cur:
                self.__check_destination_table_exists(destination_table, cur)
                self.__ingest_payload(destination_table, payload, cur)

    def __ingest_payload(
        self, destination_table: str, payload: List[dict], cur: Cursor
    ) -> None:
        fields, query = self.__create_query(destination_table, cur)

        for obj in payload:
            try:
                cur.execute(query, obj)
                log.debug("Payload was ingested.")
            except Exception as e:
                if collections.Counter(fields) != collections.Counter(obj.keys()):
                    errors.log_and_rethrow(
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
                        e,
                        wrap_in_vdk_error=True,
                    )
                elif isinstance(e, ProgrammingError):
                    errors.log_and_rethrow(
                        errors.ResolvableBy.USER_ERROR,
                        log,
                        "Failed to sent payload",
                        f"""
                        An issue with the SQL query occured. The error message
                        was: {str(e)}
                        """,
                        "Will not be able to send the payload for ingestion",
                        "See error message for help ",
                        e,
                        wrap_in_vdk_error=True,
                    )
                else:
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
        self, destination_table: str, cur: Cursor
    ) -> None:
        # https://tableplus.com/blog/2018/04/sqlite-check-whether-a-table-exists.html
        table_exists_flag = sum(
            1
            for row in cur.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{destination_table}';"
            )
        )
        if not table_exists_flag:  # check if destination_table exists in database
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                what_happened="Cannot send payload for ingestion to SQLite database.",
                why_it_happened="destination_table does not exist in the target database.",
                consequences="Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                countermeasures="Make sure the destination_table exists in the target SQLite database.",
            )

    def __create_query(self, destination_table: str, cur: Cursor) -> str:
        fields = [
            field_tuple[0]
            for field_tuple in cur.execute(
                f"SELECT name FROM PRAGMA_TABLE_INFO('{destination_table}')"
            ).fetchall()
        ]
        # the query fstring evaluates to 'INSERT INTO dest_table (val1, val2, val3) VALUES (:val1, :val2, :val3)'
        # assuming dest_table is the destination_table and val1, val2, val3 are the fields of that table
        query = f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES ({', '.join([':'+field for field in fields])})"

        return fields, query
