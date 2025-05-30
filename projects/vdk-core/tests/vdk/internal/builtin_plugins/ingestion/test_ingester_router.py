# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_router import IngesterRouter
from vdk.internal.core.config import ConfigEntry
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.errors import VdkConfigurationError
from vdk.internal.core.statestore import StateStore


def create_ingester_router(configs) -> IngesterRouter:
    config_key_value_pairs = {
        "ingester_number_of_worker_threads": ConfigEntry(value=1),
        "ingester_payload_size_bytes_threshold": ConfigEntry(value=100),
        "ingester_objects_queue_size": ConfigEntry(value=1),
        "ingester_payloads_queue_size": ConfigEntry(value=1),
        "ingester_log_upload_errors": ConfigEntry(value=False),
        "ingestion_payload_aggregator_timeout_seconds": ConfigEntry(value=2),
    }
    for i in configs.keys():
        config_key_value_pairs[i] = ConfigEntry(configs[i])
    section = {"vdk": config_key_value_pairs}
    test_config = Configuration(section)
    state_store = MagicMock(spec=StateStore)
    return IngesterRouter(test_config, state_store)


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_object_for_ingestion(mock_ingester_base: MagicMock):
    router = create_ingester_router({"ingest_method_default": "test"})
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

    with pytest.raises(VdkConfigurationError):
        router.send_object_for_ingestion({"a": "b"})

    mock_ingester_base.return_value.send_object_for_ingestion.assert_not_called()


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_send_tabular_data_for_ingestion(mock_ingester_base: MagicMock):
    router = create_ingester_router({"ingest_method_default": "test"})
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

    with pytest.raises(VdkConfigurationError):
        router.send_tabular_data_for_ingestion(rows=["b"], column_names=["a"])

    mock_ingester_base.return_value.send_tabular_data_for_ingestion.assert_not_called()


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_chained_ingest_plugins(mock_ingester_base: MagicMock):
    config = {
        "ingest_payload_preprocess_sequence": "pre-ingest-test",
        "ingest_payload_postprocess_sequence": "post-ingest-test",
        "ingest_method_default": "test",
    }

    router = create_ingester_router(config)

    # Register plugins
    router.add_ingester_factory_method(
        "pre-ingest-test", lambda: MagicMock(spec=IIngesterPlugin)
    )
    router.add_ingester_factory_method(
        "post-ingest-test", lambda: MagicMock(spec=IIngesterPlugin)
    )
    router.add_ingester_factory_method("test", lambda: MagicMock(spec=IIngesterPlugin))

    # Send data for ingestion
    router.send_object_for_ingestion({"a": "b"})

    # Verify method calls
    mock_ingester_base.return_value.send_object_for_ingestion.assert_called_with(
        {"a": "b"}, None, "test", None, None
    )
    assert len(mock_ingester_base.call_args[1]["pre_processors"]) == 1
    assert len(mock_ingester_base.call_args[1]["post_processors"]) == 1


@patch(f"{IngesterRouter.__module__}.{IngesterBase.__name__}", spec=IngesterBase)
def test_router_no_chained_ingest_plugins(mock_ingester_base: MagicMock):
    router = create_ingester_router({"ingest_method_default": "test"})

    router.add_ingester_factory_method(
        "pre-ingest-test", lambda: MagicMock(spec=IIngesterPlugin)
    )
    router.add_ingester_factory_method("test", lambda: MagicMock(spec=IIngesterPlugin))

    router.send_object_for_ingestion({"a": "b"})

    mock_ingester_base.return_value.send_object_for_ingestion.assert_called_with(
        {"a": "b"}, None, "test", None, None
    )

    assert not mock_ingester_base.call_args[1]["pre_processors"]
    assert not mock_ingester_base.call_args[1]["post_processors"]


def test_router_raise_error_chained_ingest_plugins_not_registered():
    config = {
        "ingest_payload_preprocess_sequence": "pre-ingest-test",
        "ingest_payload_postprocess_sequence": "post-ingest-test",
        "ingest_method_default": "test",
    }

    router = create_ingester_router(config)
    router.add_ingester_factory_method("test", lambda: MagicMock(spec=IIngesterPlugin))

    with pytest.raises(VdkConfigurationError):
        router.send_object_for_ingestion({"a": "b"})

    with pytest.raises(VdkConfigurationError) as exc_info:
        router.send_tabular_data_for_ingestion(rows=["b"], column_names=["a"])

    error_msg = exc_info.value
    assert "method: pre-ingest-test" in str(error_msg)
