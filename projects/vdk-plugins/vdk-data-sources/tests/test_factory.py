# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from vdk.plugin.data_sources.data_source import IDataSource
from vdk.plugin.data_sources.data_source import IDataSourceConfiguration
from vdk.plugin.data_sources.factory import data_source
from vdk.plugin.data_sources.factory import DataSourceNotFoundException
from vdk.plugin.data_sources.factory import (
    SingletonDataSourceFactory,
)


class MockDataSourceConfig(Mock, IDataSourceConfiguration):
    pass


@data_source("mock", MockDataSourceConfig)
class MockDataSource(Mock, IDataSource):
    pass


def test_register_and_list_data_source():
    with patch(
        SingletonDataSourceFactory.__module__
        + "."
        + SingletonDataSourceFactory.__name__
        + "._instance",
        None,
    ):
        factory = SingletonDataSourceFactory()

        factory.register_data_source_class(MockDataSource)

        data_sources = factory.list()
        assert len(data_sources) == 1

        factory2 = SingletonDataSourceFactory()
        assert len(factory2.list()) == 1


def test_create_data_source():
    with patch(
        SingletonDataSourceFactory.__module__
        + "."
        + SingletonDataSourceFactory.__name__
        + "._instance",
        None,
    ):
        factory = SingletonDataSourceFactory()

        factory.register_data_source_class(MockDataSource)

        data_source_instance = factory.create_data_source("mock")
        assert data_source_instance is not None


def test_create_data_source_not_foound():
    with patch(
        SingletonDataSourceFactory.__module__
        + "."
        + SingletonDataSourceFactory.__name__
        + "._instance",
        None,
    ):
        factory = SingletonDataSourceFactory()

        with pytest.raises(DataSourceNotFoundException):
            factory.create_data_source("not-found")
