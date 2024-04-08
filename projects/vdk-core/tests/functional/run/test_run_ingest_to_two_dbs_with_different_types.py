# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import duckdb
import pytest
from click.testing import CliRunner
from click.testing import Result
from vdk.plugin.duckdb import duckdb_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.fixture(scope="function")
def setup(tmpdir):
    temp_db_file = os.path.join(str(tmpdir), "test_db.duckdb")
    connection = duckdb.connect(temp_db_file)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
            "SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
            "VDK_INGEST_TARGET_DEFAULT": "DUCKDB",
            "DUCKDB_DATABASE": temp_db_file,
            "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
        },
    ):
        yield

        connection.close()
        os.remove(temp_db_file)


def test_ingest_to_two_dbs_with_different_types(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("ingest_to_two_dbs_with_different_types")]
    )

    cli_assert_equal(0, result)

    _verify_sql_ingestion(runner)
    _verify_duckdb_ingest_step()


def _verify_sql_ingestion(runner):
    actual_rs = _sql_query(runner, "SELECT * FROM stocks")
    cli_assert_equal(0, actual_rs)
    expected_data = [{"date": "2020-01-01", "symbol": "GOOG", "price": 122.0}]
    assert json.loads(actual_rs.output) == expected_data


def _verify_duckdb_ingest_step():
    # TODO: why should we use duckdb connection here instead of vdk, usability gap
    connection = duckdb.connect(os.environ["DUCKDB_DATABASE"])
    actual_rs = connection.query("SELECT * FROM test_duckdb_table")
    result_string = actual_rs.__str__()
    assert result_string.count("2021-01-01") == 1
    assert result_string.count("BOOB") == 1
    assert result_string.count("123.0") == 1
    assert result_string.count("2022-01-01") == 1
    assert result_string.count("TOOT") == 1
    assert result_string.count("124.0") == 1


def _sql_query(runner, query):
    actual_rs: Result = runner.invoke(
        ["sql-query", "-o", "json", "--query", query],
        runner=CliRunner(mix_stderr=False),
    )
    return actual_rs
