# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from unittest.mock import patch
from datetime import datetime

import pytest
from taurus.api.plugin.plugin_input import IIngesterPlugin
from taurus.vdk.builtin_plugins.ingestion.ingester_base import IngesterBase
from taurus.vdk.builtin_plugins.ingestion.ingester_configuration import (
    IngesterConfiguration,
)
from taurus.vdk.core import errors
from taurus.vdk.core.config import Configuration


def create_ingester_base() -> IngesterBase:
    config_key_value_pairs = {
        "INGESTER_NUMBER_OF_WORKER_THREADS": 1,
        "INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD": 100,
        "INGESTER_OBJECTS_QUEUE_SIZE": 1,
        "INGESTER_PAYLOADS_QUEUE_SIZE": 1,
        "INGESTER_LOG_UPLOAD_ERRORS": False,
        "INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS": 2,
    }
    test_config = Configuration(
        config_key_to_description=None, config_key_to_value=config_key_value_pairs
    )

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
        ingester_base.send_object_for_ingestion(payload=test_unserializable_payload,
                                                destination_table=destination_table,
                                                method=method,
                                                target=target)
    assert exc_info.type == errors.UserCodeError


def test_send_tabular_data_for_ingestion():
    test_rows = iter([["testrow0testcol0", 42]])
    test_columns = ["testcol0", "testcol1"]
    destination_table = "a_destination_table"
    converted_row = [
        {
            "@table": destination_table,
            "testcol0": "testrow0testcol0",
            "testcol1": 42,
        }
    ]
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
