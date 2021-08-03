# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.vdk.core.config import Configuration
from taurus.vdk.core.config import ConfigurationBuilder

INGESTER_NUMBER_OF_WORKER_THREADS = "INGESTER_NUMBER_OF_WORKER_THREADS"
INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD = "INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD"
INGESTER_OBJECTS_QUEUE_SIZE = "INGESTER_OBJECTS_QUEUE_SIZE"
INGESTER_PAYLOADS_QUEUE_SIZE = "INGESTER_PAYLOADS_QUEUE_SIZE"
INGESTER_LOG_UPLOAD_ERRORS = "INGESTER_LOG_UPLOAD_ERRORS"
INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS = (
    "INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS"
)


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

    def get_payload_aggregator_timeout_seconds(self) -> int:
        return int(
            self.__config.get_value(INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS)
        )


def add_definitions(config_builder: ConfigurationBuilder):
    # IngesterBase-related configurations
    config_builder.add(
        key=INGESTER_NUMBER_OF_WORKER_THREADS,
        default_value=10,
        description="Number of worker threads for async ingestion.",
    )
    config_builder.add(
        key=INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD,
        default_value=2097152,  # Size is limited to 2MB (2*1024*1024)
        description="""
        Aggregated payload threshold. If the combined size of two or more payloads
        passed to the `send_object_for_ingestion()` or
        `send_tabular_data_for_ingestion()` methods is below this threshold, they
        will be bundled together, before being send to the ingestion plugin.
        """,
    )
    config_builder.add(
        key=INGESTER_OBJECTS_QUEUE_SIZE,
        default_value=10000,
        description="""
        The maximum number of payloads that can be stored for ingestion at any
        given time.
        """,
    )
    config_builder.add(
        key=INGESTER_PAYLOADS_QUEUE_SIZE,
        default_value=50,
        description="""
        The maximum number of payloads that can be processed by the Versatile Data
        Kit at any given time.
        """,
    )
    config_builder.add(
        key=INGESTER_LOG_UPLOAD_ERRORS,
        default_value=True,
        description="Specifies if errors should be logged.",
    )
    config_builder.add(
        key=INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS,
        default_value=2,
        description="""
        Wait time in seconds, that a thread is waiting for receiving a payload,
        before it continues with the next one.
        """,
    )
