# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.ingestion.ingester_base import IngesterBase
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration


def create_ingester_base() -> IngesterBase:
    config_key_value_pairs = {
        "ingester_number_of_worker_threads": 1,
        "ingester_payload_size_bytes_threshold": 100,
        "ingester_objects_queue_size": 1,
        "ingester_payloads_queue_size": 1,
        "ingester_log_upload_errors": False,
        "ingestion_payload_aggregator_timeout_seconds": 2,
    }
    test_config = Configuration(None, config_key_value_pairs, {})

    return IngesterBase(
        data_job_name="test_job",
        op_id="42a420",
        ingester=MagicMock(spec=IIngesterPlugin),
        ingest_config=IngesterConfiguration(test_config),
    )


@patch.object(IngesterBase, "_send", spec=True)
def test_send_object_for_ingestion(mocked_send):
    test_unserializable_payload = {"key1": 42, "key2": datetime.utcnow()}
    destination_table = "a_destination_table"
    method = "test_method"
    target = "some_target"
    ingester_base = create_ingester_base()

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_object_for_ingestion(
            payload=None,
            destination_table=destination_table,
            method=method,
            target=target,
        )
    assert exc_info.type == errors.UserCodeError

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_object_for_ingestion(
            payload="wrong_payload_type",
            destination_table=None,
            method=method,
            target=target,
        )
    assert exc_info.type == errors.UserCodeError

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_object_for_ingestion(
            payload=test_unserializable_payload,
            destination_table=destination_table,
            method=method,
            target=target,
        )
    assert exc_info.type == errors.UserCodeError


def test_send_tabular_data_for_ingestion():
    test_rows = iter([["testrow0testcol0", 42, None]])
    test_columns = ["testcol0", "testcol1", "testcol2"]
    destination_table = "a_destination_table"
    converted_row = [{"testcol0": "testrow0testcol0", "testcol1": 42, "testcol2": None}]
    method = "test_method"
    target = "some_target"
    collection_id = "test_job|42a420"
    ingester_base = create_ingester_base()

    ingester_base.send_tabular_data_for_ingestion(
        rows=test_rows,
        column_names=test_columns,
        destination_table=destination_table,
        method=method,
        target=target,
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_with(
        payload=converted_row,
        destination_table=destination_table,
        target=target,
        collection_id=collection_id,
    )

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_tabular_data_for_ingestion(
            rows=None,
            column_names=test_columns,
            destination_table=None,
            method=method,
            target=target,
        )
    assert exc_info.type == errors.UserCodeError

    with pytest.raises(errors.UserCodeError) as exc_info:
        ingester_base.send_tabular_data_for_ingestion(
            rows=None,
            column_names={"wrong_test_columns"},
            destination_table=destination_table,
            method=method,
            target=None,
        )
    assert exc_info.type == errors.UserCodeError


def test_plugin_ingest_payload():
    test_payload = {"key1": "val1", "key2": "val2", "key3": "val3"}
    test_aggregated_payload = [{"key1": "val1", "key2": "val2", "key3": "val3"}]
    destination_table = "a_destination_table"
    method = "test_method"
    target = "some_target"
    collection_id = "test_job|42a420"
    ingester_base = create_ingester_base()

    ingester_base.send_object_for_ingestion(
        payload=test_payload,
        destination_table=destination_table,
        method=method,
        target=target,
    )
    ingester_base.close()

    ingester_base._ingester.ingest_payload.assert_called_once()
    ingester_base._ingester.ingest_payload.assert_called_with(
        payload=test_aggregated_payload,
        destination_table=destination_table,
        target=target,
        collection_id=collection_id,
    )


def test_ingest_payload_multiple_destinations():
    test_payload1 = {"key1": "val1", "key2": "val2", "key3": "val3"}
    test_payload2 = {"key1": 1, "key2": 2, "key3": 3}
    test_expected_payload1 = [{"key1": "val1", "key2": "val2", "key3": "val3"}]
    test_expected_payload2 = [{"key1": 1, "key2": 2, "key3": 3}]
    destination_table1 = "a_destination_table"
    destination_table2 = "another_destination_table"
    method = "test_method"
    target = "some_target"
    collection_id = "test_job|42a420"
    ingester_base = create_ingester_base()

    ingester_base.send_object_for_ingestion(
        payload=test_payload1,
        destination_table=destination_table1,
        method=method,
        target=target,
    )
    ingester_base.send_object_for_ingestion(
        payload=test_payload2,
        destination_table=destination_table2,
        method=method,
        target=target,
    )
    ingester_base.close()

    assert ingester_base._ingester.ingest_payload.call_count == 2

    assert ingester_base._ingester.ingest_payload.call_args_list[0] == call(
        collection_id=collection_id,
        target=target,
        destination_table=destination_table1,
        payload=test_expected_payload1,
    )

    assert ingester_base._ingester.ingest_payload.call_args_list[1] == call(
        collection_id=collection_id,
        target=target,
        destination_table=destination_table2,
        payload=test_expected_payload2,
    )
