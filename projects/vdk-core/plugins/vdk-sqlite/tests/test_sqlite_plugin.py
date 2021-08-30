# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from pytest import raises
from taurus.vdk import sqlite_plugin
from taurus.vdk.core.errors import UserCodeError
from taurus.vdk.core.errors import VdkConfigurationError
from taurus.vdk.ingest_to_sqlite import IngestToSQLite
from taurus.vdk.sqlite_connection import SQLiteConfiguration
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner
from taurus.vdk.test_utils.util_funcs import jobs_path_from_caller_directory

payload: dict = {"some_data": "some_test_data", "more_data": "more_test_data"}


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
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
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
    mock_sqlite_conf.get_default_ingest_target.return_value = (
        str(tmpdir) + "vdk-sqlite.db"
    )
    sqlite_ingester = IngestToSQLite(mock_sqlite_conf)

    with mock.patch("sqlalchemy.engine.base.Connection.execute") as conn_execute:
        sqlite_ingester.ingest_payload(
            payload=payload,
            destination_table="test_table",
        )

    assert (
        str(conn_execute.call_args_list[0][0][0])
        == "INSERT INTO test_table (some_data, more_data) VALUES (:some_data, :more_data)"
    )


def test_sqlite_ingestion_missing_target(tmpdir):
    mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
    mock_sqlite_conf.get_default_ingest_target.return_value = None
    mock_sqlite_conf.get_sqlite_file.return_value = None
    sqlite_ingester = IngestToSQLite(mock_sqlite_conf)

    with raises(VdkConfigurationError):
        sqlite_ingester.ingest_payload(payload=payload)


def test_sqlite_ingestion_missing_dest_table(tmpdir):
    mock_sqlite_conf = mock.MagicMock(SQLiteConfiguration)
    mock_sqlite_conf.get_default_ingest_target.return_value = (
        str(tmpdir) + "vdk-sqlite.db"
    )
    sqlite_ingester = IngestToSQLite(mock_sqlite_conf)

    with raises(UserCodeError):
        sqlite_ingester.ingest_payload(
            payload=payload,
            destination_table="test_table",
        )
