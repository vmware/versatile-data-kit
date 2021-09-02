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

TRINO_INGEST_BATCH_SIZE = "TRINO_INGEST_BATCH_SIZE"

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

        batch_size = self.context.core_context.configuration.get_value(
            TRINO_INGEST_BATCH_SIZE
        )

        with self.context.connections.open_connection(
            "TRINO"
        )._connect() as conn:  # TODO: fix the need for _connect()
            cur = conn.cursor()
            self.__check_destination_table_exists(destination_table, cur)
            self.__ingest_payload(destination_table, payload, cur, batch_size)

    def __ingest_payload(
        self, destination_table: str, payload: List[dict], cur: Cursor, batch_size: int
    ) -> None:
        # the max http header needs to increase for a payload of 1 million rows, here it's 10 times the default
        import http

        http.client._MAXLINE = 6553600  # TODO: verify this isn't a security vulnerability or something similar

        for lower_bound, upper_bound in self.__create_batches(len(payload), batch_size):
            query, fields = self.__create_query_and_fields(
                destination_table, cur, upper_bound - lower_bound
            )

            try:
                obj_batch = payload[lower_bound:upper_bound]
                params = tuple(obj[field] for obj in obj_batch for field in fields)
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

    def __check_destination_table_exists(
        self, destination_table: str, cur: Cursor
    ) -> None:
        """
        Validates that the destination_table exists in the target Trino database.
        If the table does not exist, an appropriate exception is raised. Otherwise,
        program execution continues.

        :param destination_table: the name of the destination table
        :param cur: the database cursor
        """
        tables = [table_tuple[0] for table_tuple in cur.execute("SHOW TABLES")]

        if (
            destination_table not in tables
        ):  # check if destination_table exists in database
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                what_happened="Cannot send payload for ingestion to Trino database.",
                why_it_happened="destination_table does not exist in the target database.",
                consequences="Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                countermeasures="Make sure the destination_table exists in the target Trino database.",
            )

    def __create_query_and_fields(
        self, destination_table: str, cur: Cursor, batch_size: int
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

        fields = [
            field_tuple[0]
            for field_tuple in cur.execute(f"SHOW COLUMNS FROM {destination_table}")
        ]

        row_to_be_replaced = f"({', '.join('?' for field in fields)})"

        return (
            f"INSERT INTO {destination_table} ({', '.join(fields)}) VALUES {', '.join([row_to_be_replaced for i in range(batch_size)])}",
            fields,
        )

    def __create_batches(self, payload_size: int, batch_size: int):
        """
        Creates index tuples which are used to slice the payload into chunks of size batch_size,
        where the last chunk may vary in size if payload_size is not perfectly divisible by batch_size
        For example, __create_batches(1420, 500) will output [(0, 500), (500, 1000), (1000, 1420)]

        :param payload_size: the size of the payload
        :param batch_size: our preferred size of batch; note that the last output batch may be smaller
        :return: a list of indexing tuples
        """

        batches = []
        current_point = 0
        while current_point + batch_size < payload_size:
            batches.append((current_point, current_point + batch_size))
            current_point += batch_size
        batches.append((current_point, payload_size))

        return batches
