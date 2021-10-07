# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_router import IngesterRouter
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.statestore import StateStore


def create_ingester_router(configs) -> IngesterRouter:
    config_key_value_pairs = {
        "INGESTER_NUMBER_OF_WORKER_THREADS": 1,
        "INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD": 100,
        "INGESTER_OBJECTS_QUEUE_SIZE": 1,
        "INGESTER_PAYLOADS_QUEUE_SIZE": 1,
        "INGESTER_LOG_UPLOAD_ERRORS": False,
        "INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS": 2,
    }
    config_key_value_pairs.update(configs)
    test_config = Configuration({}, config_key_value_pairs, {})
    state_store = MagicMock(spec=StateStore)
    return IngesterRouter(test_config, state_store)


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_object_for_ingestion(mock_ingester_base: MagicMock):
    router = create_ingester_router({"INGEST_METHOD_DEFAULT": "test"})
    router.add_ingester_factory_method("test", lambda: MagicMock(spec=IIngesterPlugin))

    router.send_object_for_ingestion({"a": "b"})

    mock_ingester_base.return_value.send_object_for_ingestion.assert_called_with(
        {"a": "b"}, None, "test", None, None
    )


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_object_for_ingestion_no_default_method(
    mock_ingester_base: MagicMock,
):
    router = create_ingester_router({})

    with pytest.raises(UserCodeError):
        router.send_object_for_ingestion({"a": "b"})

    mock_ingester_base.return_value.send_object_for_ingestion.assert_not_called()


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_tabular_data_for_ingestion(mock_ingester_base: MagicMock):
    router = create_ingester_router({"INGEST_METHOD_DEFAULT": "test"})
    router.add_ingester_factory_method("test", lambda: MagicMock(spec=IIngesterPlugin))

    router.send_tabular_data_for_ingestion(rows=["b"], column_names=["a"])

    mock_ingester_base.return_value.send_tabular_data_for_ingestion.assert_called_with(
        ["b"], ["a"], None, "test", None, None
    )


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_tabular_data_for_ingestion_no_default_method(
    mock_ingester_base: MagicMock,
):
    router = create_ingester_router({})

    with pytest.raises(UserCodeError):
        router.send_tabular_data_for_ingestion(rows=["b"], column_names=["a"])

    mock_ingester_base.return_value.send_tabular_data_for_ingestion.assert_not_called()
