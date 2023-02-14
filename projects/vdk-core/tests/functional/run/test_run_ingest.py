# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from typing import List
from typing import Optional
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.internal.builtin_plugins.ingestion.ingester_configuration import (
    INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND,
)
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


class FailingIngestIntoMemoryPlugin(IngestIntoMemoryPlugin):
    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IngestIntoMemoryPlugin.IngestionMetadata] = None,
    ):
        raise IndexError("Random error from our plugin")


def test_run_ingest():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    result: Result = runner.invoke(["run", util.job_path("ingest-job")])

    cli_assert_equal(0, result)

    expected_object = dict(
        int_key=1,
        str_key="str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )
    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    expected_rows_object = {"first": "1", "second": 2}
    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"


def test_run_ingest_fails():
    runner = CliEntryBasedTestRunner(FailingIngestIntoMemoryPlugin())

    result: Result = runner.invoke(["run", util.job_path("ingest-job")])

    cli_assert_equal(1, result)


@mock.patch.dict(os.environ, {INGESTER_WAIT_TO_FINISH_AFTER_EVERY_SEND: "true"})
def test_run_ingest_wait_after_send():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin)

    result: Result = runner.invoke(["run", util.job_path("ingest-job")])

    cli_assert_equal(0, result)

    expected_object = dict(
        int_key=1,
        str_key="str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )
    assert ingest_plugin.payloads[0].payload[0] == expected_object
    assert ingest_plugin.payloads[0].destination_table == "object_table"

    expected_rows_object = {"first": "1", "second": 2}
    assert ingest_plugin.payloads[1].payload[0] == expected_rows_object
    assert ingest_plugin.payloads[1].destination_table == "tabular_table"
