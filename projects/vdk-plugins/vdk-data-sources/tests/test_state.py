# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.data_sources.state import DataSourceState
from vdk.plugin.data_sources.state import IDataSourceState
from vdk.plugin.data_sources.state import InMemoryDataSourceStateStorage


def __data_source_state(source) -> IDataSourceState:
    storage = InMemoryDataSourceStateStorage()
    return DataSourceState(state_storage=storage, source=source)


def test_get_empty_data_source():
    assert __data_source_state("non_existent_source").read_stream("foo") == {}
    assert __data_source_state("non_existent_source").read_others("foo") == {}


def test_update_and_get_data_stream_state():
    data_source_name = "source1"
    data_stream_name = "stream1"
    new_state = {"key": "value"}

    data_source_state = __data_source_state(data_source_name)
    data_source_state.update_stream("stream", new_state)
    data_source_state.update_others("key", new_state)

    assert data_source_state.read_stream("stream") == new_state
    assert data_source_state.read_others("key") == new_state

    data_source_state.update_stream("stream", {"key": "value2"})
    data_source_state.update_others("key", {"key": "value2"})

    assert data_source_state.read_stream("stream") == {"key": "value2"}
    assert data_source_state.read_others("key") == {"key": "value2"}
