# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.data_sources.state import DataSourceState
from vdk.plugin.data_sources.state import InMemoryDataSourceStateStorage


def __data_source_state(source, stream):
    storage = InMemoryDataSourceStateStorage()
    return DataSourceState(state_storage=storage, source=source, stream=stream)


def test_get_empty_data_stream_state():
    assert (
        __data_source_state("non_existent_source", "non_existent_stream").read() == {}
    )


def test_update_and_get_data_stream_state():
    data_source_name = "source1"
    data_stream_name = "stream1"
    new_state = {"key": "value"}

    data_source_state = __data_source_state(data_source_name, data_stream_name)
    data_source_state.write(new_state)
    retrieved_state = data_source_state.read()

    assert retrieved_state == new_state
