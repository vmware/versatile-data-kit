# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from pytest import raises
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.sqlite.ingest_to_sqlite import IngestToSQLite
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


# uses the pytest tmpdir fixture - https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture
def test_sqlite_plugin(tmpdir):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )

        cli_assert_equal(0, result)

        actual_rs: Result = runner.invoke(
            ["sqlite-query", "--query", f"SELECT * FROM stocks"]
        )

        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output


def test_sqlite_ingestion(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(sqlite_plugin)
        runner.invoke(
            [
                "sqlite-query",
                "--query",
                "CREATE TABLE test_table (some_data TEXT, more_data TEXT)",
            ]
        )

        mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
        sqlite_ingester = IngestToSQLite(mock_sqlite_conf)
        payload = [{"some_data": "some_test_data", "more_data": "more_test_data"}]

        sqlite_ingester.ingest_payload(
            payload=payload,
            destination_table="test_table",
            target=db_dir,
        )

        check_result = runner.invoke(
            ["sqlite-query", "--query", "SELECT * FROM test_table"]
        )

        assert check_result.stdout == (
            "some_data       more_data\n"
            "--------------  --------------\n"
            "some_test_data  more_test_data\n"
        )


def test_sqlite_ingestion_missing_dest_table(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(sqlite_plugin)

        mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
        sqlite_ingester = IngestToSQLite(mock_sqlite_conf)

        payload = [
            {
                "str_col": "str_data",
                "int_col": 11,
                "bool_col": True,
                "bytes_col": b"bytes",
                "float_col": 1.23,
                "extra_col": None,
            },
            {
                "str_col": "str_data",
                "int_col": 11,
                "bool_col": True,
                "bytes_col": b"bytes",
                "float_col": 1.23,
                "extra_col": 1,
            },
        ]

        sqlite_ingester.ingest_payload(
            payload=payload,
            destination_table="auto_created_table",
            target=db_dir,
        )

        check_result = runner.invoke(
            ["sqlite-query", "--query", "SELECT * FROM auto_created_table"]
        )

        assert check_result.stdout == (
            "str_col      int_col    bool_col  bytes_col      float_col    extra_col\n"
            "---------  ---------  ----------  -----------  -----------  -----------\n"
            "str_data          11           1  bytes               1.23\n"
            "str_data          11           1  bytes               1.23            1\n"
        )


def test_sqlite_ingestion_column_names_mismatch(tmpdir):
    db_dir = str(tmpdir) + "vdk-sqlite.db"
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": db_dir,
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(sqlite_plugin)
        runner.invoke(
            [
                "sqlite-query",
                "--query",
                "CREATE TABLE test_table (wrong_column_name TEXT, more_data TEXT)",
            ]
        )

        mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
        sqlite_ingester = IngestToSQLite(mock_sqlite_conf)
        payload = [{"some_data": "some_test_data", "more_data": "more_test_data"}]

        with raises(UserCodeError):
            sqlite_ingester.ingest_payload(
                payload=payload,
                destination_table="test_table",
                target=db_dir,
            )
