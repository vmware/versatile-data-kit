# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import typing
from abc import abstractmethod
from typing import Any
from typing import Dict

from vdk.api.job_input import IProperties


class IDataSourceStateStorage:
    @abstractmethod
    def read(self, data_source: str) -> Dict[str, typing.Any]:
        """
        Read the state from underlying storage
        :param data_source: the data source name
        :return:
        """
        pass

    @abstractmethod
    def write(self, data_source: str, state: Dict[str, typing.Any]):
        """
        write (persist) the current state of the data source to underlying data storage.
        :param data_source:
        :param state:
        :return:
        """
        pass


class IDataSourceState:
    @abstractmethod
    def read_stream(self, stream_name: str) -> Dict[str, typing.Any]:
        """
        Read the state of a stream within a data source
        :param stream_name:
        :return:
        """

    @abstractmethod
    def update_stream(self, stream_name: str, state: Dict[str, typing.Any]):
        """
        Update the state of a stream within the datasource
        :param stream_name:
        :param state:
        :return:
        """
        pass

    @abstractmethod
    def read_others(self, key: str) -> Dict[str, typing.Any]:
        """
        Read state of a data source that is not related to streams
        :param key:
        :return:
        """
        pass

    @abstractmethod
    def update_others(self, key: str, state: Dict[str, typing.Any]):
        """
        Update state of a data source not related to streams
        :param key:
        :param state:
        :return:
        """
        pass


class DataSourceState(IDataSourceState):
    def __init__(self, state_storage: IDataSourceStateStorage, source: str):
        self._state_storage = state_storage
        self._source = source

    def __read_source(self) -> Dict[str, typing.Any]:
        source_state = self._state_storage.read(self._source)
        return source_state if source_state is not None else {}

    def read_stream(self, stream_name: str) -> Dict[str, typing.Any]:
        return self.__read_source().get("streams", {}).get(stream_name, {})

    def read_others(self, key: str) -> Dict[str, typing.Any]:
        return self.__read_source().get("others", {}).get(key, {})

    def update_stream(self, stream_name: str, state: Dict[str, typing.Any]):
        source_state = self.__read_source()
        source_state.setdefault("streams", {})[stream_name] = state
        self._state_storage.write(self._source, source_state)

    def update_others(self, key: str, state: Dict[str, typing.Any]):
        source_state = self.__read_source()
        source_state.setdefault("others", {})[key] = state
        self._state_storage.write(self._source, source_state)


class InMemoryDataSourceStateStorage(IDataSourceStateStorage):
    """
    In memory state useful for testing purposes
    """

    def __init__(self):
        self._state = {}

    def read(self, data_source: str) -> Dict[str, Any]:
        return self._state.get(data_source, {})

    def write(self, data_source: str, state: Dict[str, Any]):
        self._state[data_source] = state


class PropertiesBasedDataSourceStorage(IDataSourceStateStorage):
    KEY = ".vdk.data_sources.state"

    def __init__(self, properties: IProperties):
        self._properties = properties

    def read(self, data_source: str) -> Dict[str, Any]:
        return self._properties.get_property(
            PropertiesBasedDataSourceStorage.KEY, {}
        ).get(data_source, {})

    def write(self, data_source: str, state: Dict[str, Any]):
        all_properties = self._properties.get_all_properties()
        all_properties.setdefault(PropertiesBasedDataSourceStorage.KEY, {})[
            data_source
        ] = state
        self._properties.set_all_properties(all_properties)


class DataSourceStateFactory:
    def __init__(self, storage: IDataSourceStateStorage):
        self._storage = storage

    def get_data_source_state(self, source: str) -> IDataSourceState:
        return DataSourceState(self._storage, source)
