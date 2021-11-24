# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional
from typing import Tuple

from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.plugin.greenplum.greenplum_connection import GreenplumConnection

_log = logging.getLogger(__name__)


class IngestToGreenplum(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a Greenplum database
    """

    def __init__(self, context: JobContext):
        self._context = context

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> None:
        """
        See parent class doc for details
        """

        _log.info(
            f"Ingesting payloads to table: {destination_table} in Greenplum database; "
            f"collection_id: {collection_id}"
        )

        with self._context.connections.open_connection(
            "GREENPLUM"
        ).connect() as connection:
            cursor = connection.cursor()
            query, parameters = self._populate_query_parameters_tuple(
                destination_table, cursor, payload
            )

            try:
                cursor.execute(query, parameters)
                connection.commit()
                _log.debug("Payload was ingested.")
            except Exception as e:
                errors.log_and_rethrow(
                    errors.find_whom_to_blame_from_exception(e),
                    _log,
                    "Failed to send payload",
                    "Unknown error. Error message was : " + str(e),
                    "Will not be able to send the payload for ingestion",
                    "See error message for help ",
                    e,
                    wrap_in_vdk_error=True,
                )

    @staticmethod
    def _populate_query_parameters_tuple(
        destination_table: str, cursor: PEP249Cursor, payload: List[dict]
    ) -> (str, Tuple[str]):
        """
        Returns insert into destination table tuple of query and parameters;
        E.g. for a table dest_table with columns val1, val2 and payload size 3, this method will return:
        'INSERT INTO dest_table (val1, val2) VALUES (%s, %s), (%s, %s), (%s, %s)', ['val1', 'val2']

        :param destination_table: str
            the name of the destination table
        :param cursor: PEP249Cursor
            the database cursor
        :param payload: List[dict]
            the payloads to be ingested
        :return: Tuple[str, Tuple[str]]
            tuple containing the query and parameters
        """
        cursor.execute(f"SELECT * FROM {destination_table} WHERE false")
        columns = [c.name for c in cursor.description]

        row_placeholder = f"({', '.join('%s' for column in columns)})"

        return (
            f"INSERT INTO {destination_table} ({', '.join(columns)}) "
            f"VALUES {', '.join([row_placeholder for i in range(len(payload))])}",
            tuple(obj[column] for obj in payload for column in columns),
        )
