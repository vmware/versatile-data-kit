# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import queue
import traceback
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Callable
from typing import cast
from typing import List
from typing import Optional

from vdk.api.job_input import IIngester
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.data_source import DataSourceError
from vdk.plugin.data_sources.data_source import DataSourcePayload
from vdk.plugin.data_sources.data_source import (
    DataSourcesAggregatedException,
)
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import (
    IDataSourceErrorCallback,
)
from vdk.plugin.data_sources.data_source import IDataSourceStream
from vdk.plugin.data_sources.data_source import (
    RetryDataSourceStream,
)
from vdk.plugin.data_sources.data_source import (
    StopDataSourceStream,
)
from vdk.plugin.data_sources.state import DataSourceStateFactory
from vdk.plugin.data_sources.state import PropertiesBasedDataSourceStorage

log = logging.getLogger(__name__)


@dataclass
class IngestDestination:
    destination_table: Optional[str] = None
    method: Optional[str] = None
    target: Optional[str] = None
    collection_id: Optional[str] = None
    map_function: Optional[
        Callable[[DataSourcePayload], Optional[DataSourcePayload]]
    ] = None


@dataclass
class IngestQueueEntry:
    data_source_id: str
    stream: IDataSourceStream
    destinations: List[IngestDestination]
    error_callback: Optional[IDataSourceErrorCallback] = None


class DataSourceIngester:
    def __init__(self, job_input: IJobInput):
        self.__ingestion_queue = Queue()
        self.__actual_ingester = cast(IIngester, job_input)
        self.__worker_threads = self._start_workers(8)
        self.__being_ingested_streams = set()
        self.__stored_exceptions = queue.SimpleQueue()
        self.__state_factory = DataSourceStateFactory(
            PropertiesBasedDataSourceStorage(job_input)
        )

    def _start_workers(self, number_of_worker_threads: int) -> List[Thread]:
        threads = []
        for i in range(number_of_worker_threads):
            thread_name = f"data-source-ingest-{i}"
            t = Thread(target=self._process_ingestion_queue, name=thread_name)
            t.daemon = True
            t.start()
            threads.append(t)
        return threads

    def _process_ingestion_queue(self):
        while True:
            ingest_entry: IngestQueueEntry = self.__ingestion_queue.get()
            if self._is_termination_signal(ingest_entry):
                self.__ingestion_queue.task_done()
                break
            try:
                self._ingest_stream(ingest_entry)
            except StopDataSourceStream:
                log.debug(f"Stopping data source stream {ingest_entry.stream.name()}")
            except RetryDataSourceStream:
                log.debug(
                    f"Retrying to ingest data source stream {ingest_entry.stream.name()}"
                )
                self.__ingestion_queue.put(ingest_entry)
            except BaseException as e:
                log.exception("Ingestion failed")
                if ingest_entry.error_callback:
                    self._handle_exception(e, ingest_entry)
                else:
                    tb = traceback.extract_tb(e.__traceback__)
                    # Print only the last part of the traceback
                    last_trace = tb[-1]
                    filename = os.path.basename(last_trace.filename)
                    last_trace_message = (
                        f"{filename}:{last_trace.lineno} {last_trace.name}"
                    )

                    error_message = f"Failed to ingest stream {ingest_entry.stream.name()} with error {e} in {last_trace_message}"
                    log.warning(error_message)
                    self.__stored_exceptions.put((ingest_entry.stream.name(), e))
            finally:
                self.__ingestion_queue.task_done()

    def _handle_exception(self, e, ingest_entry):
        try:
            ingest_entry.error_callback(
                DataSourceError(data_stream=ingest_entry.stream, exception=e)
            )
        except StopDataSourceStream:
            log.debug(f"Stopping data source stream {ingest_entry.stream.name()}")
        except RetryDataSourceStream:
            log.debug(
                f"Retrying to ingest data source stream {ingest_entry.stream.name()}"
            )
            self.__ingestion_queue.put(ingest_entry)
        except BaseException as callback_exception:
            error_message = (
                f"Failed to ingest stream {ingest_entry.stream.name()} with error {e}."
                f" And error callback failed as well with error {callback_exception} "
            )
            log.warning(error_message)
            self.__stored_exceptions.put((ingest_entry.stream.name(), e))

    @staticmethod
    def _is_termination_signal(queue_item):
        return queue_item is None

    def _ingest_stream(self, ingest_entry: IngestQueueEntry):
        for payload in ingest_entry.stream.read():
            log.debug(f"Ingest payload {payload}")
            if not payload.data and not payload.state:
                log.warning(
                    f"{ingest_entry.stream.name()} returned payload without any data or state. "
                    f"This is pretty meaningless so we will skip it. But it is suspicious."
                )
                continue

            if payload.data:
                for destination in ingest_entry.destinations:
                    destination_table = self._infer_destination_table(
                        ingest_entry, destination, payload
                    )

                    payload_to_sent = DataSourcePayload(
                        payload.data, payload.metadata, payload.state, destination_table
                    )
                    if destination.map_function:
                        payload_to_sent = destination.map_function(payload_to_sent)
                        if not payload_to_sent:
                            continue

                    self.__actual_ingester.send_object_for_ingestion(
                        payload=payload_to_sent.data,
                        destination_table=payload_to_sent.destination_table,
                        method=destination.method,
                        target=destination.target,
                        collection_id=destination.collection_id,
                    )

            if payload.state:
                # TODO: it would be better to update the state after the actual ingester
                # is finished. So it might be good idea to add a callback so that when send object for ingestion
                # finishes successfully then state is updated.
                data_source_state = self.__state_factory.get_data_source_state(
                    ingest_entry.data_source_id
                )
                data_source_state.update_stream(
                    ingest_entry.stream.name(), payload.state
                )

    @staticmethod
    def _infer_destination_table(
        ingest_entry: IngestQueueEntry, destination: IngestDestination, payload
    ):
        if destination.destination_table:
            destination_table = destination.destination_table
        elif payload.destination_table:
            destination_table = payload.destination_table
        else:
            destination_table = ingest_entry.stream.name()
        return destination_table

    def start_ingestion(
        self,
        data_source_id: str,
        data_source: IDataSource,
        destinations: List[IngestDestination] = None,
        error_callback: Optional[IDataSourceErrorCallback] = None,
    ):
        if data_source_id not in self.__being_ingested_streams:
            self.__being_ingested_streams.add(data_source_id)
        else:
            raise ValueError(
                f"Data source is already in ingestion queue. "
                f"Ingestion same data source more than once is currently not supported."
            )
        if not destinations:
            destinations = [IngestDestination()]

        data_source.connect(self.__state_factory.get_data_source_state(data_source_id))

        for stream in data_source.streams():
            entry = IngestQueueEntry(
                data_source_id, stream, destinations, error_callback
            )
            self.__ingestion_queue.put(entry)

    def ingest_data_source(
        self,
        data_source_id: str,
        data_source: IDataSource,
        destination_table: Optional[str] = None,
        method: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        error_callback: Optional[IDataSourceErrorCallback] = None,
    ):
        self.start_ingestion(
            data_source_id,
            data_source,
            [IngestDestination(destination_table, method, target, collection_id)],
            error_callback,
        )

    def terminate_and_wait_to_finish(self):
        self.__ingestion_queue.join()
        self.__ingestion_queue.put(None)

    def raise_on_error(self):
        if not self.__stored_exceptions.empty():
            collected_exceptions = dict()
            while not self.__stored_exceptions.empty():
                stream_name, exception = self.__stored_exceptions.get()
                collected_exceptions[stream_name] = exception

            # Raise a custom exception that encapsulates all the stored exceptions
            raise DataSourcesAggregatedException(collected_exceptions)
