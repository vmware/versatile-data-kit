# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from decimal import Decimal
from unittest.mock import call
from unittest.mock import MagicMock

import pytest
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration

shared_test_values = {
    "test_payload1": {"key1": "val1", "key2": "val2", "key3": "val3"},
    "test_payload2": {"key1": Decimal(1), "key2": 2, "key3": 3},
    "test_expected_payload1": [{"key1": "val1", "key2": "val2", "key3": "val3"}],
    "test_expected_payload2": [{"key1": Decimal(1), "key2": 2, "key3": 3}],
    "destination_table1": "a_destination_table",
    "destination_table2": "another_destination_table",
    "method": "test_method",
    "target": "some_target",
    "collection_id": "test_job|42a420",
}


def create_ingester_base(kwargs=None, config_dict=None, ingester=None) -> IngesterBase:
    kwargs = kwargs or {}
    config_key_value_pairs = {
        "ingester_number_of_worker_threads": 1,
        "ingester_payload_size_bytes_threshold": 100,
        "ingester_objects_queue_size": 1,
        "ingester_payloads_queue_size": 1,
        "ingester_log_upload_errors": False,
        "ingestion_payload_aggregator_timeout_seconds": 2,
    }
    if config_dict is not None:
        config_key_value_pairs.update(config_dict)
    test_config = Configuration(None, config_key_value_pairs, {})

    return IngesterBase(
        data_job_name="test_job",
        op_id="42a420",
        ingester=MagicMock(spec=IIngesterPlugin) if ingester is None else ingester,
        ingest_config=IngesterConfiguration(test_config),
        **kwargs
    )


def test_send_object_for_ingestion_send_to_wait():
    ingester_base = create_ingester_base(
        config_dict={"ingester_wait_to_finish_after_every_send": True}
    )

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    assert ingester_base._ingester.ingest_payload.call_count == 1


def test_send_tabular_data_for_ingestion_send_to_wait():
    ingester_base = create_ingester_base(
        config_dict={"ingester_wait_to_finish_after_every_send": True}
    )

    ingester_base.send_tabular_data_for_ingestion(
        rows=iter([["testrow0testcol0", 42, None]]),
        column_names=["testcol0", "testcol1", "testcol2"],
        destination_table="foo",
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    assert ingester_base._ingester.ingest_payload.call_count == 1


def test_send_tabular_data_for_ingestion_send_multiple_rows():
    ingester_base = create_ingester_base(
        config_dict={
            "ingester_number_of_worker_threads": 2,
            "ingester_objects_queue_size": 3,
            "ingester_payloads_queue_size": 3,
            "ingestion_payload_aggregator_timeout_seconds": 0.5,
        }
    )

    ingester_base.send_tabular_data_for_ingestion(
        rows=iter(
            [
                ["testrow0testcol0", 12, None],
                ["testrow1testcol0", 22, None],
                ["testrow2testcol0", 32, None],
                ["testrow3testcol0", 42, None],
                ["testrow4testcol0", 52, None],
                ["testrow5testcol0", 62, None],
                ["testrow6testcol0", 72, None],
                ["testrow7testcol0", 82, None],
                ["testrow8testcol0", 92, None],
            ]
        ),
        column_names=["testcol0", "testcol1", "testcol2"],
        destination_table="foo",
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()
    assert ingester_base._ingester.ingest_payload.call_count == 9


def test_send_tabular_data_for_ingestion():
    test_rows = iter([["testrow0testcol0", 42, None]])
    test_columns = ["testcol0", "testcol1", "testcol2"]
    converted_row = [{"testcol0": "testrow0testcol0", "testcol1": 42, "testcol2": None}]
    metadata = None
    ingester_base = create_ingester_base()

    ingester_base.send_tabular_data_for_ingestion(
        rows=test_rows,
        column_names=test_columns,
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_with(
        payload=converted_row,
        destination_table=shared_test_values.get("destination_table1"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=metadata,
    )

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_tabular_data_for_ingestion(
            rows=None,
            column_names=test_columns,
            destination_table=None,
            method=shared_test_values.get("method"),
            target=shared_test_values.get("target"),
        )
    assert exc_info.type == errors.UserCodeError

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_tabular_data_for_ingestion(
            rows=None,
            column_names={"wrong_test_columns"},
            destination_table=shared_test_values.get("destination_table1"),
            method=shared_test_values.get("method"),
            target=None,
        )
    assert exc_info.type == errors.UserCodeError


def test_plugin_ingest_payload():
    metadata = None
    ingester_base = create_ingester_base()

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_once()
    ingester_base._ingester.ingest_payload.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=metadata,
    )


def test_ingest_payload_multiple_destinations():
    metadata = None
    ingester_base = create_ingester_base()

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload2"),
        destination_table=shared_test_values.get("destination_table2"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    assert ingester_base._ingester.ingest_payload.call_count == 2

    assert ingester_base._ingester.ingest_payload.call_args_list[0] == call(
        collection_id=shared_test_values.get("collection_id"),
        target=shared_test_values.get("target"),
        destination_table=shared_test_values.get("destination_table1"),
        payload=shared_test_values.get("test_expected_payload1"),
        metadata=metadata,
    )

    assert ingester_base._ingester.ingest_payload.call_args_list[1] == call(
        collection_id=shared_test_values.get("collection_id"),
        target=shared_test_values.get("target"),
        destination_table=shared_test_values.get("destination_table2"),
        payload=shared_test_values.get("test_expected_payload2"),
        metadata=metadata,
    )


def test_pre_ingestion_operation():
    pre_ingest_plugin = MagicMock(spec=IIngesterPlugin)
    ingester_base = create_ingester_base({"pre_processors": [pre_ingest_plugin]})
    ingester_base._pre_processors[0].pre_ingest_process.return_value = (
        shared_test_values.get("test_expected_payload1"),
        None,
    )

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._pre_processors[0].pre_ingest_process.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=None,
    )
    ingester_base._ingester.ingest_payload.assert_called_once()


def test_pre_ingestion_updated_dynamic_params():
    metadata = IIngesterPlugin.IngestionMetadata({})
    metadata[IIngesterPlugin.UPDATED_DYNAMIC_PARAMS] = {
        IIngesterPlugin.TARGET_KEY: "updated_target",
        IIngesterPlugin.DESTINATION_TABLE_KEY: "updated_dest_table",
    }
    pre_ingest_plugin = MagicMock(spec=IIngesterPlugin)
    ingester_base = create_ingester_base({"pre_processors": [pre_ingest_plugin]})
    ingester_base._pre_processors[0].pre_ingest_process.return_value = (
        shared_test_values.get("test_expected_payload1"),
        metadata,
    )

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._pre_processors[0].pre_ingest_process.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=None,
    )
    ingester_base._ingester.ingest_payload.assert_called_with(
        collection_id=shared_test_values.get("collection_id"),
        target="updated_target",
        destination_table="updated_dest_table",
        payload=shared_test_values.get("test_expected_payload1"),
        metadata=metadata,
    )


def test_pre_ingestion_operation_with_exceptions():
    test_exception = errors.UserCodeError("Test User Exception")
    pre_ingest_plugin = MagicMock(spec=IIngesterPlugin)
    ingester_base = create_ingester_base({"pre_processors": [pre_ingest_plugin]})

    ingester_base._pre_processors[0].pre_ingest_process.side_effect = test_exception

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._pre_processors[0].pre_ingest_process.assert_called_once()
    ingester_base._ingester.ingest_payload.assert_not_called()


def test_ingest_payload_and_post_ingestion_operation():
    test_ingestion_metadata = {"some_metadata": "some_ingestion_metadata"}
    post_ingest_plugin = MagicMock(spec=IIngesterPlugin)
    ingester_base = create_ingester_base({"post_processors": [post_ingest_plugin]})

    ingester_base._ingester.ingest_payload.return_value = test_ingestion_metadata

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_once()
    ingester_base._ingester.ingest_payload.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=None,
    )
    ingester_base._post_processors[0].post_ingest_process.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=test_ingestion_metadata,
        exception=None,
    )


def test_post_ingestion_operation_with_exceptions():
    test_exception = errors.UserCodeError("Test User Exception")
    post_ingest_plugin = MagicMock(spec=IIngesterPlugin)
    ingester_base = create_ingester_base({"post_processors": [post_ingest_plugin]})

    ingester_base._ingester.ingest_payload.side_effect = test_exception

    ingester_base.send_object_for_ingestion(
        payload=shared_test_values.get("test_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        method=shared_test_values.get("method"),
        target=shared_test_values.get("target"),
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_once()
    ingester_base._post_processors[0].post_ingest_process.assert_called_with(
        payload=shared_test_values.get("test_expected_payload1"),
        destination_table=shared_test_values.get("destination_table1"),
        target=shared_test_values.get("target"),
        collection_id=shared_test_values.get("collection_id"),
        metadata=None,
        exception=test_exception,
    )
