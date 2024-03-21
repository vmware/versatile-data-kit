# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import re
from unittest import mock
from unittest import TestCase

import pytest
from click.testing import Result
from vdk.plugin.oracle import oracle_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

DB_DEFAULT_TYPE = "DB_DEFAULT_TYPE"
ORACLE_USER = "ORACLE_USER"
ORACLE_PASSWORD = "ORACLE_PASSWORD"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"
ORACLE_THICK_MODE = "ORACLE_THICK_MODE"
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"
ORACLE_HOST = "ORACLE_HOST"
ORACLE_PORT = "ORACLE_PORT"
ORACLE_SID = "ORACLE_SID"


@pytest.mark.usefixtures("oracle_db")
@mock.patch.dict(
    os.environ,
    {
        DB_DEFAULT_TYPE: "oracle",
        ORACLE_USER: "SYSTEM",
        ORACLE_PASSWORD: "Gr0mh3llscr3am",
        ORACLE_HOST: "localhost",
        ORACLE_PORT: "1521",
        ORACLE_SID: "FREE",
        ORACLE_CONNECTION_STRING: "localhost:1521/FREE",
        ORACLE_THICK_MODE: "False",
        VDK_LOG_EXECUTION_RESULT: "True",
        VDK_INGEST_METHOD_DEFAULT: "ORACLE",
    },
)
class OracleTests(TestCase):
    def test_oracle_connect_execute(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
        )
        cli_assert_equal(0, result)
        _verify_query_execution(runner)

    def test_oracle_connect_execute_without_connection_string(self):
        backup_conn_string = os.environ["ORACLE_CONNECTION_STRING"]
        del os.environ["ORACLE_CONNECTION_STRING"]
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
        )
        cli_assert_equal(0, result)

        os.environ["ORACLE_CONNECTION_STRING"] = backup_conn_string
        _verify_query_execution(runner)

    def test_oracle_ingest_existing_table(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution(runner)

    def test_oracle_ingest_existing_table_special_chars(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job-special-chars")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_special_chars(runner)

    def test_oracle_ingest_type_inference(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job-type-inference")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_type_inference(runner)

    def test_oracle_ingest_no_table(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job-no-table")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_no_table(runner)

    def test_oracle_ingest_no_table_special_chars(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory(
                    "oracle-ingest-job-no-table-special-chars"
                ),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_no_table_special_chars(runner)

    def test_oracle_ingest_different_payloads(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("oracle-ingest-job-different-payloads"),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_different_payloads(runner)

    def test_oracle_ingest_different_payloads_no_table(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory(
                    "oracle-ingest-job-different-payloads-no-table"
                ),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_different_payloads_no_table(runner)

    def test_oracle_ingest_different_payloads_no_table_special_chars(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory(
                    "oracle-ingest-job-different-payloads-no-table-special-chars"
                ),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution_different_payloads_no_table_special_chars(runner)

    def test_oracle_ingest_blob(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("oracle-ingest-job-blob"),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_blob(runner)

    def test_oracle_ingest_nan_and_none_table(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-nan-job")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_nan_and_none_execution(runner)

    def test_oracle_ingest_data_frame_schema_inference(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory(
                    "oracle-ingest-data-frame-schema-inference"
                ),
            ]
        )
        cli_assert_equal(0, result)
        _verify_ingest_data_frame_schema_inference(runner)


def _verify_query_execution(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM todoitem"])
    expected = (
        "  ID  DESCRIPTION      DONE\n"
        "----  -------------  ------\n"
        "   1  Task 1              1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  ------------  -----------  "
        "-------------------  --------------\n"
        "   5  string              12           1.2            1  2023-11-21 "
        "08:12:53             0.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution_special_chars(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  @str_data      %int_data    *float*data*    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  -----------  -----------  --------------  -----------  "
        "-------------------  --------------\n"
        "   5  string                12             1.2            1  2023-11-21 "
        "08:12:53             0.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution_type_inference(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  STR_DATA      INT_DATA  NAN_INT_DATA      FLOAT_DATA    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  --------------  ------------  -----------  "
        "-------------------  --------------\n"
        "   5  string              12                           1.2            1  "
        "2023-11-21 08:12:53             0.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution_no_table(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  ------------  -----------  "
        "-------------------  --------------\n"
        "   0  string              12           1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
        "   1  string              12           1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
        "   2  string              12           1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution_no_table_special_chars(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  @str_data      %int_data    *float*data*    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  -----------  -----------  --------------  -----------  "
        "-------------------  --------------\n"
        "   0  string                12             1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
        "   1  string                12             1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
        "   2  string                12             1.2            1  "
        "2023-11-21T08:12:53             1.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_execution_different_payloads_no_table(runner):
    check_result = runner.invoke(
        ["sql-query", "--query", "SELECT count(*) FROM test_table"]
    )
    expected = "  COUNT(*)\n----------\n         8\n"
    assert expected in check_result.output


def _verify_ingest_execution_different_payloads_no_table_special_chars(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])

    # Skip the log lines until the line with the column headers
    log_lines = check_result.output.strip().split("\n")
    column_header_line_index = next(
        (index for index, line in enumerate(log_lines) if re.match(r"^\s*ID\s+", line)),
        None,
    )
    if column_header_line_index is None:
        raise ValueError("Column header line not found in the output.")

    actual_columns = log_lines[column_header_line_index].split()

    expected_columns = [
        "ID",
        "&timestamp_data",
        "^bool_data",
        "@int_data",
        "%float_data",
        "?str_data",
    ]
    for expected_col in expected_columns:
        assert expected_col in actual_columns

    expected_count = "  COUNT(*)\n----------\n         8\n"
    check_result = runner.invoke(
        ["sql-query", "--query", "SELECT count(*) FROM test_table"]
    )
    assert expected_count in check_result.output


def _verify_ingest_execution_different_payloads(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  TIMESTAMP_DATA\n"
        "----  ----------  ----------  ------------  -----------  "
        "-------------------\n"
        "   0\n"
        "   1  string\n"
        "   2  string              12\n"
        "   3  string              12           1.2\n"
        "   6  string              12           1.2\n"
        "   4  string              12           1.2            1\n"
        "   7  string              12           1.2            1\n"
        "   5  string              12           1.2            1  2023-11-21 "
        "08:12:53\n"
    )
    assert expected in check_result.output


def _verify_ingest_blob(runner):
    check_result = runner.invoke(
        [
            "sql-query",
            "--query",
            "SELECT utl_raw.cast_to_varchar2(dbms_lob.substr(blob_data,2000,1)) FROM test_table",
        ]
    )
    expected = (
        "UTL_RAW.CAST_TO_VARCHAR2(DBMS_LOB.SUBSTR(BLOB_DATA,2000,1))\n"
        "-------------------------------------------------------------\n"
        "The woods are lovely, dark and deep,\n"
        "But I have promises to keep,\n"
        "And miles to go before I sleep,\n"
        "And miles to go before I sleep.\n"
    )
    assert expected in check_result.output


def _verify_ingest_nan_and_none_execution(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = (
        "  ID  STR_DATA    INT_DATA    FLOAT_DATA      BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  ------------  -----------  "
        "-------------------  --------------\n"
        "   5  string                                          1  2023-11-21 "
        "08:12:53             0.1\n"
    )
    assert expected in check_result.output


def _verify_ingest_data_frame_schema_inference(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM test_table"])
    expected = "  A    B    C\n---  ---  ---\n  1    2    3\n"
    assert expected in check_result.output
