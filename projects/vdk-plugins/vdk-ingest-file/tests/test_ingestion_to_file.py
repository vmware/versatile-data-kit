# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List
from unittest.mock import mock_open
from unittest.mock import patch

from vdk.plugin.ingest_file.ingestion_to_file import IngestionToFile


def test_ingestion_to_file():
    test_destination_table: str = "test_table"
    test_payload: List[dict] = [
        {
            "@table": test_destination_table,
            "@id": "test_id",
            "some_data": "some_test_data",
        }
    ]
    test_target: str = "test_target"
    test_collection_id: str = "test_collection_id"

    mocked_open = mock_open()

    with patch("builtins.open", mocked_open):
        ingestion_plugin = IngestionToFile()
        ingestion_plugin.ingest_payload(
            payload=test_payload,
            destination_table=test_destination_table,
            target=test_target,
            collection_id=test_collection_id,
        )

    mocked_open.assert_called_with("test_target.json", "a")
    handle = mocked_open()
    handle.write.assert_called_with(
        '{\n    "@table": "test_table",\n    "@id": "test_id",\n    "some_data": "some_test_data"\n}'
    )
