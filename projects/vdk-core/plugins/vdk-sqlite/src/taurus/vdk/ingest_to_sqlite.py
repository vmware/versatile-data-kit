# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from contextlib import closing
from sqlite3 import Cursor
from typing import List
from typing import Optional

from taurus.vdk.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from taurus.vdk.core import errors
from taurus.vdk.sqlite_connection import SQLiteConfiguration
from taurus.vdk.sqlite_connection import SQLiteConnection

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
            the path to the database file; if left None, defaults to VDK_DEFAULT_INGEST_TARGET
        :param collection_id:
            an identifier specifying that data from different method invocations belongs to the same collection
        """
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
        query = self.__create_query(destination_table, cur)

        for obj in payload:
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
        # the returned fstring evaluates to 'INSERT INTO dest_table (val1, val2, val3) VALUES (:val1, :val2, :val3)'
        # assuming dest_table is the destination_table and val1, val2, val3 are the fields of that table
        return f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES ({', '.join([':'+field for field in fields])})"
