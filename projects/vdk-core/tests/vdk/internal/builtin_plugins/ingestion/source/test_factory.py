# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from vdk.internal.builtin_plugins.ingestion.source.factory import (
    DataSourceNotFoundException,
)
from vdk.internal.builtin_plugins.ingestion.source.factory import (
    SingletonDataSourceFactory,
)


def test_register_and_list_data_source():
    with patch(
        SingletonDataSourceFactory.__module__
        + "."
        + SingletonDataSourceFactory.__name__
        + "._instance",
        None,
    ):
        factory = SingletonDataSourceFactory()

        factory.register_data_source("test_ds", Mock(), Mock())

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

        factory.register_data_source("test_ds", Mock(), Mock())

        data_source_instance = factory.create_data_source("test_ds")
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
