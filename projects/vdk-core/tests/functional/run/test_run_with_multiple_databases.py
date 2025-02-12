# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from unittest import mock

import duckdb
import pytest
from click.testing import CliRunner
from click.testing import Result
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.plugin.duckdb import duckdb_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.sqlite.sqlite_connection import SQLiteConnection
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
            "VDK_FIRST_SQLITE_SQLITE_FILE": str(tmpdir) + "vdk-first-sqlite.db",
            "VDK_SECOND_SQLITE_SQLITE_FILE": str(tmpdir) + "vdk-second-sqlite.db",
            "DUCKDB_DATABASE": temp_db_file,
            "VDK_INGEST_TARGET_DEFAULT": "DUCKDB",
            "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
            "SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED": "true",
        },
    ):
        yield

        connection.close()
        os.remove(temp_db_file)


class TemplatePlugin:
    def __init__(
        self,
        template_name: str = "append",
        template_path: pathlib.Path = pathlib.Path(util.job_path("template-append")),
    ):
        self.__template_name = template_name
        self.__template_path = template_path

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.templates.add_template(self.__template_name, self.__template_path)


def test_multiple_dbs_from_different_type(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("multiple-dbs-from-different-type-job")]
    )

    cli_assert_equal(0, result)

    _verify_sqlite_query(runner)
    _verify_duckdb_query(runner)


def test_multiple_dbs_from_different_type_template_sql(setup):
    runner = CliEntryBasedTestRunner(
        duckdb_plugin,
        sqlite_plugin,
        TemplatePlugin(
            "mul-sql",
            pathlib.Path(util.job_path("template-multiple-different-dbs-sql")),
        ),
    )
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("job-using-two-different-dbs-templates"),
        ]
    )

    cli_assert_equal(0, result)

    _verify_sqlite_query(runner)
    _verify_duckdb_query(runner)


def test_multiple_dbs_from_different_type_template_ingest(setup):
    runner = CliEntryBasedTestRunner(
        duckdb_plugin,
        sqlite_plugin,
        TemplatePlugin(
            "mul-ingest",
            pathlib.Path(util.job_path("template-ingest-to-two-dbs")),
        ),
    )
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("job-ingest-to-two-dbs-templates"),
        ]
    )

    cli_assert_equal(0, result)
    _verify_sql_ingestion(runner)
    _verify_duckdb_ingest_step()


def test_multiple_dbs_from_same_type_sql(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("multiple-dbs-from-same-type-sql-job")]
    )

    cli_assert_equal(0, result)
    _verify_sqlite_query(runner)

    first_conn = SQLiteConnection(
        pathlib.Path(os.environ.get("VDK_FIRST_SQLITE_SQLITE_FILE"))
    )
    second_conn = SQLiteConnection(
        pathlib.Path(os.environ.get("VDK_SECOND_SQLITE_SQLITE_FILE"))
    )

    named_result = (
        first_conn.new_connection().cursor().execute("SELECT * FROM stocks").fetchall()
    )
    assert "VOOV" in named_result[0]
    named_result = (
        second_conn.new_connection().cursor().execute("SELECT * FROM stocks").fetchall()
    )
    assert "LOOL" in named_result[0]


def test_multiple_dbs_from_different_type_sql(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("multiple-dbs-from-different-type-sql-job"),
        ]
    )

    cli_assert_equal(0, result)

    _verify_sqlite_query(runner)
    _verify_duckdb_query(runner)


def test_multiple_dbs_from_same_type_python(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("multiple-dbs-from-same-type-python-job"),
        ]
    )

    cli_assert_equal(0, result)
    _verify_sqlite_query(runner)

    first_conn = SQLiteConnection(
        pathlib.Path(os.environ.get("VDK_FIRST_SQLITE_SQLITE_FILE"))
    )
    second_conn = SQLiteConnection(
        pathlib.Path(os.environ.get("VDK_SECOND_SQLITE_SQLITE_FILE"))
    )

    named_result = (
        first_conn.new_connection().cursor().execute("SELECT * FROM stocks").fetchall()
    )
    assert "VOOV" in named_result[0]
    named_result = (
        second_conn.new_connection().cursor().execute("SELECT * FROM stocks").fetchall()
    )
    assert "LOOL" in named_result[0]


def test_ingest_to_two_dbs_with_different_types(setup):
    runner = CliEntryBasedTestRunner(duckdb_plugin, sqlite_plugin)

    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("ingest_to_two_dbs_with_different_types"),
        ]
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


def _verify_sqlite_query(runner):
    actual_rs = _sql_query(runner, "SELECT * FROM stocks")
    cli_assert_equal(0, actual_rs)
    expected_data = [{"date": "2020-01-01", "symbol": "GOOG", "price": 122.0}]
    assert json.loads(actual_rs.output) == expected_data


def _sql_query(runner, query):
    actual_rs: Result = runner.invoke(
        ["sql-query", "-o", "json", "--query", query],
        runner=CliRunner(mix_stderr=False),
    )
    return actual_rs


def _verify_duckdb_query(runner):
    connection = duckdb.connect(os.environ["DUCKDB_DATABASE"])
    actual_rs = connection.query("SELECT * FROM stocks")
    # This is the expected actual_rs:
    # ┌────────────┬─────────┬───────┐
    # │    date    │ symbol  │ price │
    # │  varchar   │ varchar │ float │
    # ├────────────┼─────────┼───────┤
    # │ 2021-01-01 │ BOOB    │ 123.0 │
    # └────────────┴─────────┴───────┘
    result_string = actual_rs.__str__()
    assert result_string.count("2021-01-01") == 1
    assert result_string.count("BOOB") == 1
    assert result_string.count("123.0") == 1
    # check whether sqlite data is here, it should not be
    assert result_string.count("2020-01-01") == 0
    assert result_string.count("GOOG") == 0
    assert result_string.count("122.0") == 0
