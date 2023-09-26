# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import csv
import os
from sqlite3 import OperationalError
from unittest import mock

from click.testing import Result
from vdk.internal.core.errors import ResolvableByActual
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.csv import csv_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.sqlite.ingest_to_sqlite import IngestToSQLite
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
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


def test_csv_export(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin, csv_plugin)
        runner.invoke(
            [
                "sqlite-query",
                "--query",
                "CREATE TABLE test_table (some_data TEXT, more_data TEXT)",
            ]
        )

        mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
        sqlite_ingest = IngestToSQLite(mock_sqlite_conf)
        payload = [
            {"some_data": "some_test_data", "more_data": "more_test_data"},
            {"some_data": "some_test_data_copy", "more_data": "more_test_data_copy"},
        ]

        sqlite_ingest.ingest_payload(
            payload=payload,
            destination_table="test_table",
            target=db_dir,
        )
        result = runner.invoke(["export-csv", "--query", "SELECT * FROM test_table"])
        output = []
        path = os.path.abspath(os.getcwd())
        with open(os.path.join(path, "result.csv")) as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                output.append(row)
        assert output[0] == ["some_test_data", "more_test_data"]
        assert output[1] == ["some_test_data_copy", "more_test_data_copy"]


def test_export_csv_with_already_existing_file(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        path = os.path.abspath(os.getcwd())
        with open(os.path.join(path, "result2.csv"), "w"):
            runner = CliEntryBasedTestRunner(csv_plugin)
            result = runner.invoke(
                [
                    "export-csv",
                    "--query",
                    "SELECT * FROM test_table",
                    "--file",
                    "result2.csv",
                ]
            )
            assert isinstance(result.exception, UserCodeError)
            cli_assert_equal(1, result)


def test_csv_export_with_nonexistent_table(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin, csv_plugin)
        drop_table(runner, "test_table")
        result = runner.invoke(
            [
                "export-csv",
                "--query",
                "SELECT * FROM test_table",
                "--file",
                "result3.csv",
            ]
        )
        assert isinstance(result.exception, OperationalError)
        assert hasattr(result.exception, "_vdk_resolvable_actual")
        assert (
            getattr(result.exception, "_vdk_resolvable_actual")
            == ResolvableByActual.PLATFORM
        )


def test_csv_export_with_no_data(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin, csv_plugin)
        drop_table(runner, "test_table")
        runner.invoke(
            [
                "sqlite-query",
                "--query",
                "CREATE TABLE test_table (some_data TEXT, more_data TEXT)",
            ]
        )
        runner.invoke(
            [
                "export-csv",
                "--query",
                "SELECT * FROM test_table",
                "--file",
                "result4.csv",
            ]
        )
        output = []
        with open(os.path.join(os.path.abspath(os.getcwd()), "result4.csv")) as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                output.append(row)
        assert len(output) == 0


def drop_table(runner: CliEntryBasedTestRunner, table: str):
    runner.invoke(
        [
            "sqlite-query",
            "--query",
            f"DROP TABLE IF EXISTS {table}",
        ]
    )
