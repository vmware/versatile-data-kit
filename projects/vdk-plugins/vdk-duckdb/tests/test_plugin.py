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
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.fixture(scope="function")
def setup_duckdb(tmpdir):
    temp_db_file = os.path.join(str(tmpdir), "test_db.duckdb")
    connection = duckdb.connect(temp_db_file)

    with mock.patch.dict(
        os.environ,
        {
            "DB_DEFAULT_TYPE": "duckdb",
            "DUCKDB_DATABASE": temp_db_file,
            "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
        },
    ):
        yield

        connection.close()
        os.remove(temp_db_file)


def test_duckbd_plugin(setup_duckdb):
    runner = CliEntryBasedTestRunner(duckdb_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("test-duckdb-job")]
    )

    cli_assert_equal(0, result)

    _verify_sql_steps(runner)
    _verify_ingest_step(runner)


def _verify_sql_steps(runner):
    actual_rs = _sql_query(runner, "SELECT * FROM stocks")
    cli_assert_equal(0, actual_rs)
    expected_data = [
        {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
        {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
    ]
    assert json.loads(actual_rs.output) == expected_data


def _verify_ingest_step(runner):
    actual_rs = _sql_query(runner, "SELECT * FROM test_duckdb_table")
    cli_assert_equal(0, actual_rs)
    expected_data = [
        {"bool_col": 0, "dec_col": "1.234", "int_col": 2, "str_col": "str"}
    ]
    assert json.loads(actual_rs.output) == expected_data


def _sql_query(runner, query):
    actual_rs: Result = runner.invoke(
        ["sql-query", "-o", "json", "--query", query],
        runner=CliRunner(
            mix_stderr=False
        ),  # TODO: replace when CliEntryBasedTestRunner add support for it
    )
    return actual_rs
