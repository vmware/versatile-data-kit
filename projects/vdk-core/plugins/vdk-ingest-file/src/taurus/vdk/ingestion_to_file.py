# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from datetime import datetime
from typing import List
from typing import Optional

from taurus.api.plugin.plugin_input import IIngesterPlugin


log = logging.getLogger(__name__)


class IngestionToFile(IIngesterPlugin):
    """
    Create a new ingestion mechanism to ingest data into local file.
    """

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        """
        Ingest payload to file.

        :param payload: List[dict]
            A list of payloads to be ingested.
        :param destination_table: Optional[string]
            Optional argument. A string indicating the table in the database, where
            the data will be ingested.
        :param target: Optional[string]
            Optional argument. Used to specify the name of the file, where the data
            will be ingested.
        :param collection_id: Optional[string]
            Optional argument. Currently not used.
        """
        json_object = None

        if not target:
            target = f"table.{datetime.utcnow()}.json"

        with open(f"{target}.json", "a") as f:
            for obj in payload:
                try:
                    json_object = json.dumps(obj, indent=4)
                except Exception as e:
                    log.warning(
                        "Payload could not be converted to json. "
                        f"Exception was: {e} "
                        "Payload would be ingested as is."
                    )

                if not json_object:
                    json_object = str(payload)

                try:
                    f.write(json_object)
                except (ValueError, OSError) as e:
                    log.error(
                        "An error occurred while ingesting data" f"Exception was: {e}"
                    )
