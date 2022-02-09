# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

INGESTER_NUMBER_OF_WORKER_THREADS = "INGESTER_NUMBER_OF_WORKER_THREADS"
INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD = "INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD"
INGESTER_OBJECTS_QUEUE_SIZE = "INGESTER_OBJECTS_QUEUE_SIZE"
INGESTER_PAYLOADS_QUEUE_SIZE = "INGESTER_PAYLOADS_QUEUE_SIZE"
INGESTER_LOG_UPLOAD_ERRORS = "INGESTER_LOG_UPLOAD_ERRORS"
INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS = (
    "INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS"
)
INGESTER_SHOULD_RAISE_EXCEPTION_ON_FAILURE = (
    "INGESTER_SHOULD_RAISE_EXCEPTION_ON_FAILURE"
)
INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND = "INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND"


class IngesterConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_number_of_worker_threads(self) -> int:
        return int(self.__config.get_value(INGESTER_NUMBER_OF_WORKER_THREADS))

    def get_payload_size_bytes_threshold(self) -> int:
        return int(self.__config.get_value(INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD))

    def get_objects_queue_size(self) -> int:
        return int(self.__config.get_value(INGESTER_OBJECTS_QUEUE_SIZE))

    def get_payloads_queue_size(self) -> int:
        return int(self.__config.get_value(INGESTER_PAYLOADS_QUEUE_SIZE))

    def get_should_log_upload_errors(self) -> bool:
        return bool(self.__config.get_value(INGESTER_LOG_UPLOAD_ERRORS))

    def get_should_raise_exception_on_failure(self) -> bool:
        return bool(self.__config.get_value(INGESTER_SHOULD_RAISE_EXCEPTION_ON_FAILURE))

    def get_payload_aggregator_timeout_seconds(self) -> int:
        return int(
            self.__config.get_value(INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS)
        )

    def get_wait_to_finish_after_every_send(self) -> bool:
        return bool(self.__config.get_value(INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND))


def add_definitions(config_builder: ConfigurationBuilder):
    # IngesterBase-related configurations
    config_builder.add(
        key=INGESTER_NUMBER_OF_WORKER_THREADS,
        default_value=10,
        description="Number of worker threads for async ingestion.",
    )
    config_builder.add(
        key=INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD,
        default_value=500 * 1024,  # Set default to 500KB
        description="""
        Aggregated payload threshold in bytes (when uncompressed). If the combined size of two or more payloads
        passed to the `send_object_for_ingestion()` or
        `send_tabular_data_for_ingestion()` methods is below this threshold, they
        will be bundled together, before being send to the ingestion plugin.
        Ingester make sure to send batches of data in approximately that size.
        Adjust size so that it is optimize for ingestion method. For example in Kafka 1KB may be better value.
        This is similar to INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS and INGESTER_PAYLOADS_QUEUE_SIZE.
        """,
    )
    config_builder.add(
        key=INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS,
        default_value=2,
        description="""
        Wait time in seconds, that a ingester thread is waiting for receiving a payload, before it continues with the next one.
        If payloads sit in the queue more than specified time they'd be bundled together and send to the ingestion plugin.
        This is similar to INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD and INGESTER_PAYLOADS_QUEUE_SIZE.
        """,
    )
    config_builder.add(
        key=INGESTER_PAYLOADS_QUEUE_SIZE,
        default_value=50,
        description="""
        If the number of payloads buffer reach this limit, they'd be bundled together and send to the ingestion plugin.
        This is similar to INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD and INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS.
        """,
    )
    config_builder.add(
        key=INGESTER_OBJECTS_QUEUE_SIZE,
        default_value=10000,
        description="""
        The maximum number of payloads that can be stored for ingestion at any
        given time. When limit is reach send_*_for_ingestion method would effctively block unitl the queue is freed.
        """,
    )
    config_builder.add(
        key=INGESTER_LOG_UPLOAD_ERRORS,
        default_value=True,
        description="Specifies if errors should be logged.",
    )
    config_builder.add(
        key=INGESTER_SHOULD_RAISE_EXCEPTION_ON_FAILURE,
        default_value=True,
        description="When set to true, if there is an ingesting error, and we fail to ingest some data,"
        " ingester will raise an exception at the end - during finalize_job phase (plugin hook)."
        "By default this will cause the data job to fail (this behaviour can be overridden by plugins).",
    )
    config_builder.add(
        key=INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND,
        default_value=False,
        description="Data is send in background asynchronously. "
        "By default after the data is queued, the send method "
        "(send_object_for_ingestion and send_tabular_data_for_ingestion)"
        " returns and does not wait for the actual transfer/processing. "
        "VDK ingester framework will wait and block the whole job at the end only. "
        "Set this to True and the send methods will block "
        "until the data is processed and ingested by VDK before proceeding."
        "If there is an error the send methods will not fail. "
        "The job will fail at the end if INGESTER_SHOULD_RAISE_EXCEPTION_ON_FAILURE is set",
    )
