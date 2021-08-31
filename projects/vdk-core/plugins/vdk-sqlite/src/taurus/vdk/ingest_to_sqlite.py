# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

from sqlalchemy import column
from sqlalchemy import insert
from sqlalchemy import table
from sqlalchemy.dialects import sqlite
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
    ):
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

        conn = SQLiteConnection(target).new_connection()
        cur = conn.cursor()

        # checking if the table exists - https://tableplus.com/blog/2018/04/sqlite-check-whether-a-table-exists.html
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

        # create target TableClause
        dest_table_clause = table(
            destination_table, *(column(key) for key in payload[0].keys())
        )

        for obj in payload:
            try:
                query = str(dest_table_clause.insert())
                cur.execute(query, obj)
                conn.commit()
                log.debug("Payload was ingested.")
            except Exception as e:
                conn.close()
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
        conn.close()
