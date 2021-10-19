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
        Do the actual ingestion of the payload

        :param payload: List[dict]
            The payloads to be ingested. Depending on the number of payloads to be
            processed, there might 0 or many dict objects. Each dict object is a
            separate payload.
            Note: The memory size of the list is dependent on the
            payload_size_bytes_threshold attribute.
        :param destination_table: Optional[string]
            (Optional) The name of the table, where the data should be ingested into.
            This argument is optional, and needs to be considered only when the name
            of the destination table is not included in the payload itself.
        :param target: Optional[string]
            (Optional) Used to identify where the data should be ingested into.
                Specifies a data source and its destination database.
                The values for this parameter can be in the format
                `<some-data-source_and-db-table>`, or as a URL.
                Example: http://example.com/<some-api>/<data-source_and-db-table>
            This parameter does not need to be used, in case the
            `INGEST_TARGET_DEFAULT` environment variable is set. This can be made by
            plugins, which may set default value, or it can be overwritten by users.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different method
            invocations belong to same collection. Defaults to "data_job_name|OpID",
            meaning all method invocations from a data job run will belong to the
            same collection.
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
