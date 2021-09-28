# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.csv import csv_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import IngestIntoMemoryPlugin


def _get_file(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_METHOD_DEFAULT": "memory"},
)
def test_ingestion_csv():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, csv_plugin)

    result: Result = runner.invoke(["ingest-csv", "-f", _get_file("test.csv")])
    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
    assert len(ingest_plugin.payloads[0].payload) == 4
    expected_first_row = {
        "Transaction_date": "01/02/2009 04:53",
        "Product": "Product1",
        "Price": 1200,
        "Latitude": 39.195,
        "Longitude": -94.68194,
        "US Zip": 8056,
    }
    assert ingest_plugin.payloads[0].payload[0] == expected_first_row


@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_METHOD_DEFAULT": "memory"},
)
def test_ingestion_csv_with_target_table():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, csv_plugin)

    result: Result = runner.invoke(
        ["ingest-csv", "-f", _get_file("test.csv"), "-t", "table_name"]
    )
    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
    assert ingest_plugin.payloads[0].destination_table == "table_name"


@mock.patch.dict(
    os.environ,
    {"VDK_INGEST_METHOD_DEFAULT": "memory"},
)
def test_ingestion_csv_with_options():
    ingest_plugin = IngestIntoMemoryPlugin()
    runner = CliEntryBasedTestRunner(ingest_plugin, csv_plugin)

    result: Result = runner.invoke(
        [
            "ingest-csv",
            "-f",
            _get_file("test.csv"),
            "-o",
            '{"dtype": {"US Zip": "str"}}',
        ]
    )
    cli_assert_equal(0, result)

    assert len(ingest_plugin.payloads) > 0
    assert ingest_plugin.payloads[0].payload[0]["US Zip"] == "08056"
