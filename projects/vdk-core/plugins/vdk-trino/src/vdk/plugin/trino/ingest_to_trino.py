# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

from trino.dbapi import Cursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors

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
            this parameter is currently unused
            TODO: figure out what to use target for
        :param collection_id:
            an identifier specifying that data from different method invocations belongs to the same collection
        """

        log.info(
            f"Ingesting payloads to table: {destination_table} in Trino database; "
            f"collection_id: {collection_id}"
        )

        with self.context.connections.open_connection("TRINO").connect() as conn:
            cur = conn.cursor()
            self._ingest_payload(destination_table, cur, payload)

    def _ingest_payload(
        self, destination_table: str, cur: Cursor, payload: List[dict]
    ) -> None:
        # the max http header needs to increase for a payload of 1 million rows, here it's 10 times the default
        import http

        http.client._MAXLINE = 6553600

        query, fields = self._create_query_and_fields(
            destination_table, len(payload), cur
        )

        try:
            params = tuple(obj[field] for obj in payload for field in fields)
            cur.execute(query, params)
            cur.fetchall()
            log.debug("Payload was ingested.")
        except Exception as e:
            errors.log_and_rethrow(
                errors.find_whom_to_blame_from_exception(e),
                log,
                "Failed to sent payload",
                "Unknown error. Error message was : " + str(e),
                "Will not be able to send the payload for ingestion",
                "See error message for help ",
                e,
                wrap_in_vdk_error=True,
            )

    def _create_query_and_fields(
        self, destination_table: str, payload_size: int, cur: Cursor
    ) -> (str, List[str]):
        """
        Returns a tuple of the insert query and the list of fields in the destination table;
        for a table dest_table with fields val1, val2 and batch_size 3, this method will return:
        'INSERT INTO dest_table (val1, val2) VALUES (?, ?), (?, ?), (?, ?)', ['val1', 'val2']

        :param destination_table: the name of the destination table
        :param cur: the database cursor
        :param batch_size: the size of the batch of rows to be ingested
        :return: a tuple containing the query and list of fields
        """

        cur.execute(f"SHOW COLUMNS FROM {destination_table}")
        fields = [field_tuple[0] for field_tuple in cur.fetchall()]

        row_to_be_replaced = f"({', '.join('?' for field in fields)})"

        return (
            f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES {', '.join([row_to_be_replaced for i in range(payload_size)])}",
            fields,
        )
