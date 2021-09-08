# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List
from typing import Optional

import requests
from taurus.vdk.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from taurus.vdk.core import errors

log = logging.getLogger(__name__)


class IngestOverHttp(IIngesterPlugin):
    """
    Create a new ingestion mechanism
    """

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: str = None,
        collection_id: Optional[str] = None,
    ):
        header = {"Content-Type": "application/octet-stream"}  # TODO: configurable

        log.info(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        # Check if target is passed
        if not target:
            errors.log_and_throw(
                errors.ResolvableBy.CONFIG_ERROR,
                log,
                what_happened="Cannot send payload for ingestion over http.",
                why_it_happened="target has not been provided to the plugin. "
                "Most likely it has been mis-configured",
                consequences="Will not be able to send the payloads and will throw exception."
                "Likely the job would fail",
                countermeasures="Make sure you have set correct target - "
                "either as VDK_DEFAULT_INGEST_TARGET configuration variable "
                "or passed target to send_**for_ingestion APIs",
            )

        # TODO: do not make separate http requests for each payload but send them in single http request
        for obj in payload:
            # TODO: Move all ingestion formatting logic to a separate plugin.
            if not ("@table" in obj):
                if not destination_table:
                    errors.log_and_throw(
                        errors.ResolvableBy.USER_ERROR,
                        log,
                        "Corrupt payload",
                        """destination_table argument is empty, or @table key is
                        missing from payload.""",
                        "Payload would not be ingested, and data job may fail.",
                        "Re-send payload by including @table key/value pair, or pass a destination_table parameter to the ingestion method called.",
                    )
                else:
                    obj["@table"] = destination_table

            try:
                req = requests.post(
                    url=target,
                    json=obj,
                    headers=header,
                    verify=False,  # nosec # TODO: disabled temporarily for easier testing, it must be configurable
                )
                if 400 <= req.status_code < 500:
                    errors.log_and_throw(
                        errors.ResolvableBy.USER_ERROR,
                        log,
                        "Failed to sent payload",
                        f"HTTP Client error. status is {req.status_code} and message was : {req.text}",
                        "Will not be able to send the payload for ingestion",
                        "Fix the error and try again ",
                    )
                if req.status_code >= 500:
                    errors.log_and_throw(
                        errors.ResolvableBy.PLATFORM_ERROR,
                        log,
                        "Failed to sent payload",
                        f"HTTP Server error. status is {req.status_code} and message was : {req.text}",
                        "Will not be able to send the payload for ingestion",
                        "Re-try the operation again. If error persist contact support team. ",
                    )
                log.debug(
                    "Payload was ingested. Request Details: "
                    f"Status Code: {req.status_code}, \nPayload: {req.text}"
                )
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
