# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from vdk.plugin.data_sources.config import is_config_class
from vdk.plugin.data_sources.state import IDataSourceState


class IDataSourceConfiguration:
    """
    Interface representing the configuration for a data source.

    It's part of a definition of a data source - what configuraiton it requires.
    You need to implement a class and decoreated with @config_class decorator like this:

    Example::

    # Configuration for StackOverflow data source to interact with its API and extract data.
    @config_class(name="stackoverflow-api", description="Extract data from StackOverflow API")
    class StackOverflowDataSourceConfiguration(IDataSourceConfiguration):
        api_url: str = config_field(description="StackOverflow API URL")
        api_key: Optional[str] = config_field(description="API key", default="")
        api_endpoints: List[str] = config_field(
            description="List of API endpoints", default=['answers', 'questions', 'posts']
        )
        ...

    """

    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls)
        if not is_config_class(new_class):
            raise TypeError(f"Class {cls} must be decorated with @config_class")
        return new_class


@dataclass(frozen=True)
class DataSourcePayload:
    """
    Encapsulates a single payload to be ingested coming from a data source.

    :param data: The data to be ingested.
    :param metadata: Additional metadata about the data.
    :param state: Optional state related to the data (for the timestamp or id of the payload) which will be peristed once the payload is sucessfully ingested
    """

    data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Union[int, str, bool, float, datetime]]]
    state: Optional[Dict[str, Any]] = field(default_factory=dict)
    destination_table: Optional[str] = None


class StopDataSourceStream(Exception):
    """Signal the end of a stream and there's no more data"""


class RetryDataSourceStream(Exception):
    """Signal the stream ingestion should be retried"""


class IDataSourceStream:
    """
    Abstract class for a Data Source Stream, representing a channel or resource to read data.

    For example each table in a database could be a stream.
    Or each separate API endpoint for an API could be a stream and so on.

    :Example::

        # Implement the data extraction from StackOverflow API
        class StackOverflowDataSourceStream(IDataSourceStream):

            def __init__(self, endpoint_url: str):
                self._endpoint_url = endpoint_url

            def read(self) -> Iterator[DataSourcePayload]:
                for item in stackoverflow_client.get(self._endpoint_url):
                    yield DataSourcePayload(item)

    """

    @abstractmethod
    def name(self) -> str:
        """
        :return: unique (within the data souce) name of the data source stream which can be used as a key and find by it.
        """
        pass

    @abstractmethod
    def read(self) -> Iterable[DataSourcePayload]:
        """
        Generator method or Iterator for reading data from the stream.

        :return: An iterable of DataSourcePayload objects.

        """
        pass


class IDataSource:
    """
    Abstract class for a Data Source, responsible for managing the connection and providing data streams.

    :Example::

        # Let's build data source for Stack Overflow API. We will split each API endpoint data into separate stream

        @data_source(name="stackoverflow-api",
                     config_class=StackOverflowDataSourceConfiguration)
        class StackOverflowDataSource(IDataSource):

            def configure(self, config: IDataSourceConfiguration):
                self._config = config

            def connect(self, state: IDataSourceState):
                if not self._streams:
                    self._streams = [StackOverflowDataSourceStream(endpoint) for endpoint in self._config.api_endpoints]

            def streams(self) -> List[IDataSourceStream]:
                return self._streams

            def disconnect(self):
                close_all_streams(self._streams)
                self._streams = []

    """

    @abstractmethod
    def configure(self, config: IDataSourceConfiguration):
        """
        Configure the data source.

        :param config: Data source configuration object.
            In datasource subclass you are encourages to use the specific subclass config as type hint.
        """

    @abstractmethod
    def connect(self, state: Optional[IDataSourceState]):
        """
        Establish a connection using provided configuration and last saved state.

        :param state: Data source state object.
        """

    @abstractmethod
    def disconnect(self):
        """
        Disconnect and clean up resources if needed.
        """

    @abstractmethod
    def streams(self) -> List[IDataSourceStream]:
        """
        Get the available streams for this data source.

        :return: List of IDataSourceStream objects.
        """


class DataSourcesAggregatedException(Exception):
    """
    Exception to aggregate multiple Data Sources failures.

    :Example::

        DataSourcesAggregatedException({"Stream1": Exception1, "Stream2": Exception2})
    """

    def __init__(self, data_streams_exceptions: Dict[str, Exception]):
        super().__init__(
            f"Data Sources failed to ingest data: {data_streams_exceptions}"
        )
        self.data_streams_exceptions = data_streams_exceptions


@dataclass
class DataSourceError:
    """
    Data class to encapsulate information about a Data Source ingestion error.

    :data_stream: The data stream where the error occurred.
    :exception: The exception that was raised.

    :Example::

        DataSourceError(data_stream=MyStream(), exception=SomeException())

    """

    data_stream: IDataSourceStream
    exception: BaseException


class IDataSourceErrorCallback:
    """
    Callback interface to be implemented for handling data source ingestion errors.

    Example::

        # can be a function
        def my_error_callback(error: DataSourceError):
            print(f"Stream: {error.data_stream.name()}, Exception: {error.exception}")

        # or class
        class MyErrorCallback(IDataSourceErrorCallback)

            def __call__(self, error: DataSourceError):
                print(f"Stream: {error.data_stream.name()}, Exception: {error.exception}")

    """

    @abstractmethod
    def __call__(self, error: DataSourceError):
        """
        Invoked when an error occurs during data ingestion.

        :param error:DataSourceError: Object containing details of the occurred error.

        :raises:
            StopDataSourceStream: Stops the current data stream without any errors
            RetryDataSourceStream: Retries ingesting the current data stream later
        """

    pass


class IDataMetricsBatchAnalyzer:
    """
    Implement metrics analyzer for given data source.
    This will be called for each payload.
    The implementation must provide constructor without arguments
    """

    def analyze_batch(self, payload: DataSourcePayload):
        """
        Analyze the payload as it's being collected.

        :param DataSourcePayload:
        :return:
        """


class IDataMetricsFullAnalyzer:
    """
    Implement metrics analyzer for given data source.
    This will be called after the data source is exhausted
    The implementation must provide constructor without arguments
    """

    def get_data_store_target(self) -> str:
        """
        This is the ingestion target where the data would be stored for further analysis
        """
        pass

    def get_data_store_method(self) -> str:
        """
        This is the ingestion method which will be used to store the data  for further analysis
        :return:
        """
        pass

    def analyze_at_the_end(self):
        """
        Does the actual analysis on the stored data.
        To use this you must also specify data store method and data store target.
        :return:
        """
