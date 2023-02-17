# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import gzip
import logging
import sys
from typing import Dict
from typing import List
from typing import NewType
from typing import Optional

import requests
import simplejson as json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors

log = logging.getLogger(__name__)
IngestionResult = NewType("IngestionResult", Dict)


class IngestOverHttp(IIngesterPlugin):
    """
    Create a new ingestion mechanism
    """

    def __init__(self, context: JobContext):
        self._connect_timeout_seconds = (
            int(
                context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_CONNECT_TIMEOUT_SECONDS"
                )
            )
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_CONNECT_TIMEOUT_SECONDS"
            )
            else None
        )
        self._read_timeout_seconds = (
            int(
                context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_READ_TIMEOUT_SECONDS"
                )
            )
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_READ_TIMEOUT_SECONDS"
            )
            else None
        )
        self._verify = context.core_context.configuration.get_value(
            "INGEST_OVER_HTTP_VERIFY"
        )
        self._cert_file_path = context.core_context.configuration.get_value(
            "INGEST_OVER_HTTP_CERT_FILE_PATH"
        )
        self._compression_threshold_bytes = (
            int(
                context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES"
                )
            )
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_COMPRESSION_THRESHOLD_BYTES"
            )
            else None
        )
        self._compression_encoding = context.core_context.configuration.get_value(
            "INGEST_OVER_HTTP_COMPRESSION_ENCODING"
        )
        self._retry_total = (
            int(
                context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_RETRY_TOTAL"
                )
            )
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_RETRY_TOTAL"
            )
            else None
        )
        self._retry_backoff_factor = (
            float(
                context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_RETRY_BACKOFF_FACTOR"
                )
            )
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_RETRY_BACKOFF_FACTOR"
            )
            else None
        )
        self._retry_status_forcelist = (
            [
                int(s)
                for s in context.core_context.configuration.get_value(
                    "INGEST_OVER_HTTP_RETRY_STATUS_FORCELIST"
                ).split(",")
            ]
            if context.core_context.configuration.get_value(
                "INGEST_OVER_HTTP_RETRY_STATUS_FORCELIST"
            )
            else None
        )
        self._allow_nan = context.core_context.configuration.get_value(
            "INGEST_OVER_HTTP_ALLOW_NAN"
        )

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=self._retry_total,
                backoff_factor=self._retry_backoff_factor,
                allowed_methods=False,  # retry on all (including post)
                status_forcelist=self._retry_status_forcelist,
            )
        )
        self._session = requests.Session()
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)  # nosec

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> Optional[IngestionResult]:
        header = {"Content-Type": "application/octet-stream"}  # TODO: configurable

        log.debug(
            f"Ingesting payloads for target: {target}; "
            f"collection_id: {collection_id}"
        )

        self.__verify_target(target)
        self.__amend_payload(payload, destination_table)
        return self.__send_data(payload, target, header)

    @staticmethod
    def __verify_target(target):
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
                "either as VDK_INGEST_TARGET_DEFAULT configuration variable "
                "or passed target to send_**for_ingestion APIs",
            )

    @staticmethod
    def __amend_payload(payload, destination_table):
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

    def __send_data(self, data, http_url, headers) -> IngestionResult:
        data = json.dumps(data, allow_nan=self._allow_nan)
        uncompressed_size_in_bytes = sys.getsizeof(data)
        compressed_size_in_bytes = None

        if (
            self._compression_threshold_bytes
            and uncompressed_size_in_bytes >= self._compression_threshold_bytes
        ):
            headers["Content-encoding"] = "gzip"
            data = gzip.compress(data.encode(self._compression_encoding))
            compressed_size_in_bytes = sys.getsizeof(data)

        try:
            req = self._session.post(
                url=http_url,
                data=data,
                headers=headers,
                timeout=(self._connect_timeout_seconds, self._read_timeout_seconds),
                cert=self._cert_file_path,
                verify=self._verify,
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
            return IngestionResult(
                {
                    "uncompressed_size_in_bytes": uncompressed_size_in_bytes,
                    "compressed_size_in_bytes": compressed_size_in_bytes,
                    "http_status": req.status_code,
                }
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
