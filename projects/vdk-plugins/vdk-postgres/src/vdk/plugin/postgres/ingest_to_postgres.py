# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.internal.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)


class IngestToPostgres(IIngesterPlugin):
    """
    Create a new ingestion mechanism for ingesting to a database
    """

    def __init__(self, context: JobContext):
        self._context = context

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> None:
        """
        See parent class doc for details
        """

        log.info(
            f"Ingesting payloads to table: {destination_table} in database; "
            f"collection_id: {collection_id}"
        )

        # this is managed connection, no need to close it here.
        connection = self._context.connections.open_connection("POSTGRES")
        with closing_noexcept_on_close(connection.cursor()) as cursor:
            query, parameters = self._populate_query_parameters_tuple(
                destination_table, cursor, payload
            )

            try:
                cursor.executemany(
                    query, parameters
                )  # Use executemany for bulk insertion
                connection.commit()
                log.debug("Payload was ingested.")
            except Exception as e:
                errors.report(errors.find_whom_to_blame_from_exception(e), e)
                raise e

    @staticmethod
    def _populate_query_parameters_tuple(
        destination_table: str, cursor: PEP249Cursor, payload: List[dict]
    ) -> (str, list):
        """
        Prepare the SQL query and parameters for bulk insertion.

        Returns insert into destination table tuple of query and parameters;
        E.g. for a table dest_table with columns val1, val2 and payload size 2, this method will return:
        'INSERT INTO dest_table (val1, val2) VALUES (%s, %s)',
        [('val1', 'val2'), ('val1', 'val2')]
        """
        cursor.execute(f"SELECT * FROM {destination_table} WHERE false")
        columns = [desc[0] for desc in cursor.description]

        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {destination_table} ({', '.join(columns)}) VALUES ({placeholders})"

        parameters = []
        for obj in payload:
            row = tuple(obj[column] for column in columns)
            parameters.append(row)

        return query, parameters
