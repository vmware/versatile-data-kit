# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from typing import List
from unittest import mock
from unittest.mock import mock_open
from unittest.mock import patch

from click.testing import Result
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND,
)
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS,
)
from vdk.plugin.ingest_file import ingest_file_plugin
from vdk.plugin.ingest_file.ingestion_to_file import IngestionToFile
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


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


@mock.patch.dict(
    os.environ,
    {
        INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND: "true",
        INGESTION_PAYLOAD_AGGREGATOR_TIMEOUT_SECONDS: "10",
    },
)
def test_ingestion_to_file_arrow(tmpdir):
    runner = CliEntryBasedTestRunner(ingest_file_plugin)

    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("test-job"),
            "--arguments",
            json.dumps({"test_method": "file-arrow", "test_target": str(tmpdir)}),
        ]
    )

    cli_assert_equal(0, result)

    tmp_path = pathlib.Path(str(tmpdir))
    created_files = list(tmp_path.iterdir())
    cli_assert(len(created_files) > 0, result)
