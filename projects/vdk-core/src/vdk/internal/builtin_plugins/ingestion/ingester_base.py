# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import queue
import sys
import threading
from collections import defaultdict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from vdk.api.job_input import IIngester
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.ingestion import ingester_utils
from vdk.internal.builtin_plugins.ingestion.exception import (
    EmptyPayloadIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import IngestionException
from vdk.internal.builtin_plugins.ingestion.exception import (
    InvalidArgumentsIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import (
    InvalidPayloadTypeIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import (
    JsonSerializationIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import (
    PostProcessPayloadIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.exception import (
    PreProcessPayloadIngestionException,
)
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from vdk.internal.builtin_plugins.ingestion.ingester_utils import AtomicCounter
from vdk.internal.builtin_plugins.ingestion.ingester_utils import DecimalJsonEncoder
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy

log = logging.getLogger(__name__)


class IngesterBase(IIngester):
    """
    Plugins can subclass this class to provide different ingestion capabilities.
    This can be done by overriding `ingest_payload`, and provide customizations as
    to what data formats can be send, and what methods for sending are to be used.

    Sending internal telemetry for payloads can be facilitated by using `send` to
    send the telemetry payload.

    The thread pools are provided by vdk and can be customized by the plugins.
    """

    def __init__(
        self,
        data_job_name: str,
        op_id: str,
        ingester: IIngesterPlugin,
        ingest_config: IngesterConfiguration,
        pre_processors: Optional[List[IIngesterPlugin]] = None,
        post_processors: Optional[List[IIngesterPlugin]] = None,
    ):
        """
        This constructor must be called by inheritors.

        :param data_job_name: string
            Name of the data job.
        :param op_id: string
            OpId of the data job run.
        :param ingest_config: IngesterConfiguration
            Configuration related to the core ingestion API.
        :param pre_processors: Optional[List[IIngesterPlugin]]
            A list of initialized IIngesterPlugin instances, whose purpose
            is to process the payload before it is ingested.
        :param post_processors: Optional[List[IIngesterPlugin]]
            A list of initialized IIngesterPlugin instances, whose purpose
            is to process the ingestion metadata after the ingestion of the
            payload.
        """
        self._data_job_name = data_job_name
        self._op_id = op_id
        self._ingester = ingester
        self._pre_processors = pre_processors
        self._post_processors = post_processors
        self._number_of_worker_threads = ingest_config.get_number_of_worker_threads()
        self._payload_size_bytes_threshold = (
            ingest_config.get_payload_size_bytes_threshold()
        )
        self._log_upload_errors = ingest_config.get_should_log_upload_errors()

        self._payload_aggregator_timeout_seconds = (
            ingest_config.get_payload_aggregator_timeout_seconds()
        )

        self._fail_count = AtomicCounter()
        self._plugin_errors = defaultdict(
            AtomicCounter
        )  # something like {UserCodeError: 10, VdkConfigurationError: 2}
        self._success_count = AtomicCounter()
        self._closed = AtomicCounter()
        self._objects_queue: queue.Queue = queue.Queue(
            ingest_config.get_objects_queue_size()
        )
        self._payloads_queue: queue.Queue = queue.Queue(
            ingest_config.get_payloads_queue_size()
        )
        self._exception_on_failure = (
            ingest_config.get_should_raise_exception_on_failure()
        )
        self._wait_to_finish_after_every_send = (
            ingest_config.get_wait_to_finish_after_every_send()
        )

        self._start_workers()

    def send_object_for_ingestion(
        self,
        payload: dict,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        """
        See parent doc
        """
        if collection_id is None:
            collection_id = "{data_job_name}|{execution_id}".format(
                data_job_name=self._data_job_name, execution_id=self._op_id
            )

        self._send(
            payload_dict=payload,
            destination_table=destination_table,
            method=method,
            target=target,
            collection_id=collection_id,
        )

        self.__wait_if_necessary()

    def send_tabular_data_for_ingestion(
        self,
        rows: iter,
        column_names: list,
        destination_table: Optional[str],
        method: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        """
        See parent doc
        """
        if len(column_names) == 0 and destination_table is None:
            errors.report_and_throw(
                exception=InvalidArgumentsIngestionException(
                    param_name="column_names or destination_table",
                    param_constraint="non empty at least one of them",
                    actual_value="",
                ),
                resolvable_by=ResolvableBy.USER_ERROR,
            )

        if not isinstance(column_names, Iterable):
            errors.report_and_throw(
                exception=InvalidArgumentsIngestionException(
                    param_name="column_names",
                    param_constraint="iterable or list or array type",
                    actual_value=str(type(column_names)),
                ),
                resolvable_by=ResolvableBy.USER_ERROR,
            )

        if not ingester_utils.is_iterable(rows):
            errors.report_and_throw(
                exception=InvalidArgumentsIngestionException(
                    param_name="rows",
                    param_constraint="iterable type",
                    actual_value=str(type(rows)),
                ),
                resolvable_by=ResolvableBy.USER_ERROR,
            )

        log.debug(
            "Posting for ingestion data for table {table} with columns {columns} against endpoint {endpoint}".format(
                table=destination_table, columns=column_names, endpoint=target
            )
        )

        if collection_id is None:
            collection_id = "{data_job_name}|{execution_id}".format(
                data_job_name=self._data_job_name, execution_id=self._op_id
            )
            log.debug(f"Automatically generate collection id: {collection_id}")

        # fetch data in chunks to prevent running out of memory
        for page_number, page in enumerate(ingester_utils.get_page_generator(rows)):
            ingester_utils.validate_column_count(
                page, column_names, destination_table, target
            )
            converted_rows = ingester_utils.convert_table(page, column_names)
            log.debug(
                "Posting page {number} with {size} rows for ingestion.".format(
                    number=page_number, size=len(converted_rows)
                )
            )
            for row in converted_rows:
                self.__verify_payload_format(payload_dict=row)
                self._send(
                    payload_dict=row,
                    destination_table=destination_table,
                    method=method,
                    target=target,
                    collection_id=collection_id,
                )

        self.__wait_if_necessary()

    def _send(
        self,
        payload_dict: dict,
        destination_table: str,
        method: str,
        target: str,
        collection_id: str = None,
    ):
        """
        Send payload to the _objects_queue for processing.)

        :param payload_dict: dict
            Payload to be send to the _objects_queue.
        :param destination_table: string
            The name of the table, where the data should be ingested into.
        :param method: string
            Indicates the ingestion method to be used. E.g.:
                    method="file" -> ingest to file
                    method="http" -> ingest using HTTP POST requests
                    method="kafka" -> ingest to kafka endpoint
        :param target: string
            Used to identify where the data should be ingested into.
                The value for this parameter depends on the ingest method chosen.
                For "http" method, it would require an HTTP URL.
                    Example: http://example.com/<some>/<api>/<endpoint>
                For "file" method, it would require a file name or path.

                See chosen ingest method (ingestion plugin) documentation for more details on the expected target format.
        :param collection_id: string
            (Optional) An identifier to indicate that data from different method
            invocations belong to same collection. Defaults to "data_job_name|OpID",
            meaning all method invocations from a data job run will belong to the same collection.
        """
        self._objects_queue.put(
            (payload_dict, destination_table, method, target, collection_id)
        )

    def _payload_aggregator_thread(self):
        """
        Thread aggregating the ingestion data based on the provided payload size
        threshold and target/collection_id
        """
        aggregated_payload = []
        number_of_payloads = 0
        current_payload_size_in_bytes = 0
        current_target = None
        current_collection_id = None
        current_destination_table = None
        method = None
        while self._closed.value == 0:
            try:
                (
                    payload_dict,
                    destination_table,
                    method,
                    target,
                    collection_id,
                ) = self._objects_queue.get(
                    timeout=self._payload_aggregator_timeout_seconds
                )
            except queue.Empty:
                (
                    aggregated_payload,
                    number_of_payloads,
                    current_payload_size_in_bytes,
                ) = self._queue_payload_for_posting(
                    aggregated_payload,
                    number_of_payloads,
                    current_destination_table,
                    method,
                    current_target,
                    current_collection_id,
                )
                continue

            # First payload will determine the target and collection_id
            if (
                not current_target
                and not current_collection_id
                and not current_destination_table
            ):
                current_target = target
                current_collection_id = collection_id
                current_destination_table = destination_table

            # When we get a payload with different than current target/collection_id/destination_table,
            # send the current payload and start aggregating for the new one.
            if (
                current_target != target
                or current_collection_id != collection_id
                or current_destination_table != destination_table
            ):
                (
                    aggregated_payload,
                    number_of_payloads,
                    current_payload_size_in_bytes,
                ) = self._queue_payload_for_posting(
                    aggregated_payload,
                    number_of_payloads,
                    current_destination_table,
                    method,
                    current_target,
                    current_collection_id,
                )
                current_target = target
                current_collection_id = collection_id
                current_destination_table = destination_table

            # We are converting to string to get correct memory size. This may
            # cause performance issues.
            # TODO: Propose a way to calculate the object's memory footprint without converting to string.
            string_payload = str(payload_dict)

            if (
                sys.getsizeof(string_payload) + current_payload_size_in_bytes
                > self._payload_size_bytes_threshold
            ):
                (
                    aggregated_payload,
                    number_of_payloads,
                    current_payload_size_in_bytes,
                ) = self._queue_payload_for_posting(
                    aggregated_payload,
                    number_of_payloads,
                    current_destination_table,
                    method,
                    current_target,
                    current_collection_id,
                )
            aggregated_payload.append(payload_dict)
            number_of_payloads += 1
            current_payload_size_in_bytes += sys.getsizeof(string_payload)

    def _queue_payload_for_posting(
        self,
        aggregated_payload: list,
        number_of_payloads: int,
        destination_table: str,
        method: str,
        target: str,
        collection_id: str,
    ):
        """
        Send payload to the _payloads_queue.

        :param aggregated_payload: list
            List of aggregated payloads that are ready for final processing.
        :param number_of_payloads: int,
            Number of payloads to be dequeued from the _objects_queue.
        :param destination_table: string
            The name of the table, where the data should be ingested into.
        :param method: string
            Indicates the ingestion method to be used. E.g.:
                    method="file" -> ingest to file
                    method="http" -> ingest using HTTP POST requests
                    method="kafka" -> ingest to kafka endpoint
        :param collection_id: string
            An identifier to indicate that data from different method
            invocations belong to same collection. Defaults to "data_job_name|OpID",
            meaning all method invocations from a data job run will belong to the
            same collection.
        :param target: string
            Used to identify where the data should be ingested into.
                The value for this parameter depends on the ingest method chosen.
                For "http" method, it would require an HTTP URL.
                    Example: http://example.com/<some>/<api>/<endpoint>
                For "file" method, it would require a file name or path.

                See chosen ingest method (ingestion plugin) documentation for more details on the expected target format.
        """
        if aggregated_payload:
            try:
                self._payloads_queue.put(
                    (
                        aggregated_payload,
                        destination_table,
                        method,
                        target,
                        collection_id,
                    )
                )
            except Exception as e:
                self._fail_count.increment()
                if self._log_upload_errors:
                    log.warning(
                        "Failed to send a payload for ingestion. One or more rows were not ingested.\n"
                        "Exception was: {}".format(str(e))
                    )
            finally:
                for i in range(number_of_payloads):
                    self._objects_queue.task_done()
        # Return statement below is coupled with _payload_aggregator_thread
        # and is used to reset the aggregated payload, number of payloads and
        # its aggregated payload size
        aggregated_payload_reset: list = []
        number_of_payloads_reset: int = 0
        current_payload_size_in_bytes_reset: int = 0
        return (
            aggregated_payload_reset,
            number_of_payloads_reset,
            current_payload_size_in_bytes_reset,
        )

    def _payload_poster_thread(self):
        """
        Thread doing final data preparation (adding additional metadata, telemetry
        data, etc.) and ingesting the data.
        """
        while self._closed.value == 0:
            try:
                ingestion_metadata: Optional[IIngesterPlugin.IngestionMetadata] = None
                exception: Optional[Exception] = None
                payload_obj: Optional[List] = None
                destination_table: Optional[str] = None
                target: Optional[str] = None
                collection_id: Optional[str] = None
                try:
                    payload = self._payloads_queue.get()
                    payload_obj, destination_table, _, target, collection_id = payload

                    # If there are any pre-processors set, pass the payload object
                    # through them.
                    if self._pre_processors:
                        payload_obj, ingestion_metadata = self._pre_process_payload(
                            payload=payload_obj,
                            destination_table=destination_table,
                            target=target,
                            collection_id=collection_id,
                            metadata=ingestion_metadata,
                        )

                    # Verify payload after pre-processing it, since this preprocessing might be responsible for
                    # making it serializable
                    for payload_dict in payload_obj:
                        self.__verify_payload_format(payload_dict=payload_dict)

                    if ingestion_metadata:
                        updated_dynamic_params: Optional[dict] = ingestion_metadata.pop(
                            IIngesterPlugin.UPDATED_DYNAMIC_PARAMS, None
                        )
                        if updated_dynamic_params:
                            destination_table = (
                                updated_dynamic_params.get(
                                    IIngesterPlugin.DESTINATION_TABLE_KEY
                                )
                                or destination_table
                            )
                            target = (
                                updated_dynamic_params.get(IIngesterPlugin.TARGET_KEY)
                                or target
                            )
                            collection_id = (
                                updated_dynamic_params.get(
                                    IIngesterPlugin.COLLECTION_ID_KEY
                                )
                                or collection_id
                            )

                    ingestion_metadata = self._ingester.ingest_payload(
                        payload=payload_obj,
                        destination_table=destination_table,
                        target=target,
                        collection_id=collection_id,
                        metadata=ingestion_metadata,
                    )

                    self._success_count.increment()

                except Exception as e:
                    self._fail_count.increment()
                    if self._log_upload_errors:
                        # TODO: When working on row count telemetry we can add the exact number of rows not ingested.
                        log.warning(
                            "Failed to ingest a payload. "
                            "One or more rows were not ingested.\n"
                            "Exception was: {}".format(str(e))
                        )
                    exception = e
                finally:
                    self._payloads_queue.task_done()

                # If there are any post-processors set, complete the post-process
                # operations
                if self._post_processors:
                    self._execute_post_process_operations(
                        payload=payload_obj,
                        destination_table=destination_table,
                        target=target,
                        collection_id=collection_id,
                        metadata=ingestion_metadata,
                        exception=exception,
                    )
            except Exception as e:
                resolvable_by = errors.get_exception_resolvable_by(e)
                self._plugin_errors[resolvable_by].increment()

    def _start_workers(self):
        """
        Start the worker threads.
        """
        t = threading.Thread(
            target=self._payload_aggregator_thread, name="payload-aggregator"
        )
        t.daemon = True
        t.start()
        for i in range(self._number_of_worker_threads):
            thread_name = f"payload-poster{i}"
            t = threading.Thread(target=self._payload_poster_thread, name=thread_name)
            t.daemon = True
            t.start()

    def __wait_if_necessary(self):
        if self._wait_to_finish_after_every_send:
            self.__wait_to_finish()

    def __wait_to_finish(self):
        """
        Wait for completion of processing of all data added to the payload
        queue.
        """
        ingester_utils.wait_completion(
            objects_queue=self._objects_queue, payloads_queue=self._payloads_queue
        )

    def close(self):
        """
        Wait for completion of processing of all data added to the payload
        queue and then log the ingestion statistics.
        """
        self.__wait_to_finish()
        self.close_now()

    def close_now(self):
        """
        Close immediately. The method will not wait for the active queue items to get processed.
        """
        if self._closed.get_and_increment() == 0:
            if self._exception_on_failure:
                self.__handle_results()

            log.info(
                "Ingester statistics: \n\t\t"
                f"Successful uploads: {self._success_count}\n\t\t"
                f"Failed uploads: {self._fail_count}\n\t\t"
                f"Ingesting plugin errors: {'None' if not self._plugin_errors else dict(self._plugin_errors)}\n\t\t"
            )

    def _pre_process_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
        metadata: Optional[IIngesterPlugin.IngestionMetadata],
    ) -> Tuple[List[dict], Optional[IIngesterPlugin.IngestionMetadata]]:
        for plugin in self._pre_processors:
            try:
                payload, metadata = plugin.pre_ingest_process(
                    payload=payload,
                    destination_table=destination_table,
                    target=target,
                    collection_id=collection_id,
                    metadata=metadata,
                )
            except Exception as e:
                raise PreProcessPayloadIngestionException(
                    payload_id="",
                    destination_table=destination_table,
                    target=target,
                    message="Failed to pre-process the data."
                    f"User Error occurred. Exception was: {e}"
                    "Execution of the data job will fail, "
                    "in order to prevent data corruption."
                    "Check if the data sent for ingestion "
                    "is aligned with the requirements, "
                    "and that the pre-process plugins are "
                    "configured correctly.",
                    resolvable_by=ResolvableBy.USER_ERROR,
                ) from e

        return payload, metadata

    def _execute_post_process_operations(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str],
        collection_id: Optional[str],
        metadata: Optional[IIngesterPlugin.IngestionMetadata],
        exception: Optional[Exception],
    ):
        for plugin in self._post_processors:
            try:
                metadata = plugin.post_ingest_process(
                    payload=payload,
                    destination_table=destination_table,
                    target=target,
                    collection_id=collection_id,
                    metadata=metadata,
                    exception=exception,
                )
            except Exception as e:
                raise PostProcessPayloadIngestionException(
                    payload_id="",
                    destination_table=destination_table,
                    target=target,
                    message="Could not complete post-ingestion process."
                    f"Exception was: {e}"
                    "Execution of the data job will fail, "
                    "in order to prevent data corruption."
                    "Check if the data sent for "
                    "post-processing "
                    "is aligned with the requirements, "
                    "and that the post-process plugins are "
                    "configured correctly.",
                    resolvable_by=ResolvableBy.USER_ERROR,
                ) from e

    def __handle_results(self):
        final_resolvable_by = None
        if self._plugin_errors.get(ResolvableBy.USER_ERROR, AtomicCounter(0)).value > 0:
            final_resolvable_by = ResolvableBy.USER_ERROR
        elif (
            self._plugin_errors.get(ResolvableBy.CONFIG_ERROR, AtomicCounter(0)).value
            > 0
        ):
            final_resolvable_by = ResolvableBy.CONFIG_ERROR
        elif (
            self._plugin_errors.get(ResolvableBy.PLATFORM_ERROR, AtomicCounter(0)).value
            > 0
            or self._fail_count.value > 0
        ):
            final_resolvable_by = ResolvableBy.PLATFORM_ERROR

        if final_resolvable_by:
            raise IngestionException(
                message="Failed to post all data for ingestion successfully. "
                "Some data will not be ingested."
                "Check all logs carefully, there should be warnings or errors related to ingestion "
                "indicating the root cause.",
                resolvable_by=final_resolvable_by,
            )

    def __verify_payload_format(self, payload_dict: dict):
        if not payload_dict:
            raise EmptyPayloadIngestionException(resolvable_by=ResolvableBy.USER_ERROR)

        elif not isinstance(payload_dict, dict):
            raise InvalidPayloadTypeIngestionException(
                payload_id=ingester_utils.get_payload_id_for_debugging(payload_dict),
                expected_type="dict",
                actual_type=str(type(payload_dict)),
                resolvable_by=ResolvableBy.USER_ERROR,
            )

        # Check if payload dict is valid json
        # TODO: optimize the check - we should not need to serialize the payload every time
        try:
            json.dumps(payload_dict, cls=DecimalJsonEncoder)
        except (TypeError, OverflowError, Exception) as e:
            errors.report_and_throw(
                JsonSerializationIngestionException(
                    payload_id=ingester_utils.get_payload_id_for_debugging(
                        payload_dict
                    ),
                    original_exception=e,
                    resolvable_by=ResolvableBy.USER_ERROR,
                )
            )
