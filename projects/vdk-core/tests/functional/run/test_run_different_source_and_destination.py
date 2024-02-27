# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0

import json
import os
import re
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
            "VDK_INGEST_TARGET_DEFAULT": "DUCKDB",
            "DUCKDB_DATABASE": temp_db_file,
            "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
        },
    ):
        yield

        connection.close()
        os.remove(temp_db_file)


def test(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("different-db-conn-and-ingest-target")]
    )

    cli_assert_equal(0, result)

    _verify_sql_steps(runner)
    _verify_ingest_step()


def _verify_sql_steps(runner):
    actual_rs = _sql_query(runner, "SELECT * FROM stocks")
    cli_assert_equal(0, actual_rs)
    expected_data = [
        {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
        {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
    ]
    assert json.loads(actual_rs.output) == expected_data


def _verify_ingest_step():
    # TODO: why should we use duckdb connection here instead of vdk, usability gap
    connection = duckdb.connect(os.environ["DUCKDB_DATABASE"])
    actual_rs = connection.query("SELECT * FROM test_duckdb_table")
    """
    This is the expected actual_rs:
    ┌─────────┬─────────┬──────────┬─────────┐
    │ str_col │ int_col │ bool_col │ dec_col │
    │ varchar │  int32  │  int32   │ varchar │
    ├─────────┼─────────┼──────────┼─────────┤
    │ str     │       2 │        0 │ 1.234   │
    └─────────┴─────────┴──────────┴─────────┘
    """

    pattern = r"│\s*(\w+)\s*│\s*(\d+)\s*│\s*(\d+)\s*│\s*([\d.]+)\s*│"

    match = re.search(pattern, actual_rs.__str__())

    if match:
        str_col, int_col, bool_col, dec_col = match.groups()

        expected_values = {
            "str_col": "str",
            "int_col": "2",
            "bool_col": "0",
            "dec_col": "1.234",
        }

        actual_values = {
            "str_col": str_col,
            "int_col": int_col,
            "bool_col": bool_col,
            "dec_col": dec_col,
        }

        assert actual_values == expected_values


def _sql_query(runner, query):
    actual_rs: Result = runner.invoke(
        ["sql-query", "-o", "json", "--query", query],
        runner=CliRunner(mix_stderr=False),
    )
    return actual_rs
