# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from contextlib import closing
from typing import List
from typing import Optional

from taurus.vdk.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core import errors
from trino.dbapi import Cursor

log = logging.getLogger(__name__)


class IngestToTrino(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a Trino database
    """

    def __init__(self, context: JobContext):
        self.context = context

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
            the path to the database file
        :param collection_id:
            an identifier specifying that data from different method invocations belongs to the same collection
        """
        log.info(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        with self.context.connections.open_connection("TRINO") as conn:
            with closing(conn.cursor()) as cur:
                self.__check_destination_table_exists(destination_table, cur)
                self.__ingest_payload(destination_table, payload, cur)

    def __ingest_payload(
        self, destination_table: str, payload: List[dict], cur: Cursor
    ) -> None:
        query, fields = self.__create_query_and_fields(destination_table, cur)

        for obj in payload:
            try:
                params = [obj[field] for field in fields]
                cur.execute(query, params)
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
        table_tuples = cur.execute("SHOW TABLES").fetchall()
        log.info("Table tuples: ", table_tuples)
        table_exists_flag = destination_table in [
            table_tuple[0] for table_tuple in table_tuples
        ]

        if not table_exists_flag:  # check if destination_table exists in database
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                what_happened="Cannot send payload for ingestion to Trino database.",
                why_it_happened="destination_table does not exist in the target database.",
                consequences="Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                countermeasures="Make sure the destination_table exists in the target Trino database.",
            )

    def __create_query_and_fields(self, destination_table: str, cur: Cursor) -> str:
        field_tuples = cur.execute(f"SHOW COLUMNS FROM {destination_table}").fetchall()
        log.info("Field tuples: ", field_tuples)
        fields = [field_tuple[0] for field_tuple in field_tuples]
        # the returned fstring evaluates to 'INSERT INTO dest_table (val1, val2, val3) VALUES (?, ?, ?)'
        # assuming dest_table is the destination_table and val1, val2, val3 are the fields of that table
        return (
            f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES ({', '.join(['?' for field in fields])})",
            fields,
        )
