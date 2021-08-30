# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from taurus.vdk.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core import errors

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

        host = self.context.core_context.configuration.get_required_value()

        log.info(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        # create database engine
        engine = create_engine("trino://" + target)
        meta = MetaData()
        meta.reflect(bind=engine)

        if (
            destination_table not in meta.tables.keys()
        ):  # check if destination_table exists in database
            errors.log_and_throw(
                errors.ResolvableBy.USER_ERROR,
                log,
                what_happened="Cannot send payload for ingestion to SQLite database.",
                why_it_happened="destination_table does not exist in the target database.",
                consequences="Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                countermeasures="Make sure the destination_table exists in the target SQLite database.",
            )

        conn = engine.connect()

        for obj in payload:
            try:
                conn.execute(meta.tables[destination_table].insert().values(obj))
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
