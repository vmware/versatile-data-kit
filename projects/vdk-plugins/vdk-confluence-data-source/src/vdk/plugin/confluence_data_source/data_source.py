from typing import List, Iterator

from vdk.plugin.data_sources.config import config_class, config_field
from vdk.plugin.data_sources.data_source import IDataSourceConfiguration, IDataSource, IDataSourceStream, \
    DataSourcePayload
from vdk.plugin.data_sources.factory import data_source
from vdk.plugin.data_sources.state import IDataSourceState


@config_class(name="confluence-data-source", description="VDK data source plugin for Confluence")
class ConfluenceDataSourceDataSourceConfiguration(IDataSourceConfiguration):
    pass
    # TODO: add config options
    # <field-name>: str = config_field(description="...")


@data_source(
    name="confluence-data-source", config_class=ConfluenceDataSourceDataSourceConfiguration
)
class ConfluenceDataSourceDataSource(IDataSource):
    """
    Data source who is only generating some dummy data for testing purposes.
    """

    def __init__(self):
        self._config = None
        self._streams = []

    def configure(self, config: ConfluenceDataSourceDataSourceConfiguration):
        self._config = config

    def connect(self, state: IDataSourceState):
        if not self._streams:
            # TODO: populate which whatever streams are gong to be returned
            self._streams.append(ConfluenceDataSourceDataSourceStream(...))

    def disconnect(self):
        # TODO: if needed add disconnection logic
        self._streams = []

    def streams(self) -> List[IDataSourceStream]:
        return self._streams



class ConfluenceDataSourceDataSourceStream(IDataSourceStream):
    """
    THe data source stream is where teh actual data is being read.
    """

    def name(self) -> str:
        return # TODO: name of the stream. Must be unique within the data source. Should be alphanumeric.

    def __init__(self, ...):
        self... = ... # TODO: pass appropriate arguments to the stream

    def read(self) -> Iterator[DataSourcePayload]:
        # TODO: it's time to implement your main data reading logic
        # Not a bad idea is to use yield
        # while (more_data):
        #     yield DataSourcePayload(...)
        pass
