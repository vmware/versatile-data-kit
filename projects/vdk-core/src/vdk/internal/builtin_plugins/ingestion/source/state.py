# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import typing
from abc import abstractmethod
from typing import Any
from typing import Dict

from vdk.api.job_input import IProperties


class IDataSourceStateStorage:
    @abstractmethod
    def read(self) -> Dict[str, typing.Any]:
        pass

    @abstractmethod
    def write(self, state: Dict[str, typing.Any]):
        pass


class IDataSourceState:
    @abstractmethod
    def read(self) -> Dict[str, typing.Any]:
        pass

    @abstractmethod
    def write(self, state: Dict[str, typing.Any]):
        pass


class DataSourceState(IDataSourceState):
    def __init__(
        self, state_storage: IDataSourceStateStorage, source: str, stream: str
    ):
        self._state_storage = state_storage
        self._source = source
        self._stream = stream

    def read(self):
        state = self._state_storage.read()
        source_state = state.get(self._source, {})
        return source_state.get(self._stream, {})

    def write(self, state: Dict[str, typing.Any]):
        all_sources_state = self._state_storage.read()
        source_state = all_sources_state.setdefault(self._source, {})
        source_state[self._stream] = state
        self._state_storage.write(all_sources_state)


class InMemoryDataSourceStateStorage(IDataSourceStateStorage):
    """
    In memory state useful for testing purposes
    """

    def __init__(self):
        self._state = {}

    def read(self) -> Dict[str, Any]:
        return self._state

    def write(self, state: Dict[str, Any]):
        self._state = state


class PropertiesBasedDataSourceStorage(IDataSourceStateStorage):
    KEY = ".vdk.data_sources.state"

    def __init__(self, properties: IProperties):
        self._properties = properties

    def read(self) -> Dict[str, Any]:
        return self._properties.get_property(PropertiesBasedDataSourceStorage.KEY, {})

    def write(self, state: Dict[str, Any]):
        all_properties = self._properties.get_all_properties()
        all_properties[PropertiesBasedDataSourceStorage.KEY] = state
        self._properties.set_all_properties(all_properties)
