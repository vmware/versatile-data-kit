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


# @pytest.mark.usefixtures("oracle_db")
@mock.patch.dict(
    os.environ,
    {
        DB_DEFAULT_TYPE: "oracle",
        ORACLE_USER: "ADMIN",
        ORACLE_PASSWORD: "Gr0mh3llscr3am",
        #        ORACLE_HOST: "localhost",
        #        ORACLE_PORT: "1521",
        #        ORACLE_SID: "FREE",
        ORACLE_CONNECTION_STRING: "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=ge975b87ba26804_pydb_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))",
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

    #    def test_oracle_connect_execute_without_connection_string(self):
    #        backup_conn_string = os.environ["ORACLE_CONNECTION_STRING"]
    #        del os.environ["ORACLE_CONNECTION_STRING"]
    #        runner = CliEntryBasedTestRunner(oracle_plugin)
    #        result: Result = runner.invoke(
    #            ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
    #        )
    #        cli_assert_equal(0, result)
    #
    #        os.environ["ORACLE_CONNECTION_STRING"] = backup_conn_string
    #        _verify_query_execution(runner)

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

    def test_oracle_case_sensitive_columns(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("oracle-ingest-job-case-sensitive"),
            ]
        )
        cli_assert_equal(0, result)
        _verify_case_sensitive_columns(runner)


def _verify_query_execution(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM todoitem"])
    expected = [
        "  ID  DESCRIPTION      DONE\n",
        "----  -------------  ------\n",
        "   1  Task 1              1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
    expected = [
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  TIMESTAMP_DATA         DECIMAL_DATA\n",
        "----  ----------  ----------  ------------  -----------  -------------------  --------------\n",
        "   5  string              12           1.2            1  2023-11-21 08:12:53             0.1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution_special_chars(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
    expected = [
        "  ID  @STR_DATA      %INT_DATA    *FLOAT*DATA*    BOOL_DATA  TIMESTAMP_DATA         DECIMAL_DATA\n",
        "----  -----------  -----------  --------------  -----------  -------------------  --------------\n",
        "   5  string                12             1.2            1  2023-11-21 08:12:53             0.1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution_type_inference(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
    expected = [
        "  ID  STR_DATA      INT_DATA  NAN_INT_DATA      FLOAT_DATA    BOOL_DATA  TIMESTAMP_DATA         DECIMAL_DATA\n",
        "----  ----------  ----------  --------------  ------------  -----------  -------------------  --------------\n",
        "   5  string              12                           1.2            1  2023-11-21 08:12:53             0.1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution_no_table(runner):
    check_result = runner.invoke(["sql-query", "--query", 'SELECT * FROM "test_table"'])
    expected = [
        "  id  str_data      int_data    float_data    bool_data  timestamp_data         decimal_data\n",
        "----  ----------  ----------  ------------  -----------  -------------------  --------------\n",
        "   0  string              12           1.2            1  2023-11-21T08:12:53             1.1\n",
        "   1  string              12           1.2            1  2023-11-21T08:12:53             1.1\n",
        "   2  string              12           1.2            1  2023-11-21T08:12:53             1.1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution_no_table_special_chars(runner):
    check_result = runner.invoke(["sql-query", "--query", 'SELECT * FROM "test_table"'])
    expected = [
        "  id  @str_data      %int_data    *float*data*    bool_data  timestamp_data         decimal_data\n",
        "----  -----------  -----------  --------------  -----------  -------------------  --------------\n",
        "   0  string                12             1.2            1  2023-11-21T08:12:53             1.1\n",
        "   1  string                12             1.2            1  2023-11-21T08:12:53             1.1\n",
        "   2  string                12             1.2            1  2023-11-21T08:12:53             1.1\n",
    ]
    for row in expected:
        assert row in check_result.output


def _verify_ingest_execution_different_payloads_no_table(runner):
    expected_columns = [
        "COLUMN_NAME     DATA_TYPE       DATA_SCALE\n",
        "--------------  ------------  ------------\n",
        "id              NUMBER\n",
        "float_data      FLOAT\n",
        "int_data        NUMBER\n",
        "str_data        VARCHAR2\n",
        "timestamp_data  TIMESTAMP(6)             6\n",
        "bool_data       NUMBER                   0\n",
    ]
    check_result = runner.invoke(
        [
            "sql-query",
            "--query",
            "SELECT column_name, data_type, data_scale FROM user_tab_columns where table_name = 'test_table'",
        ]
    )
    for line in expected_columns:
        assert line in check_result.output

    expected_columns = ["  COUNT(*)\n", "----------\n", "         8\n"]
    check_result = runner.invoke(
        ["sql-query", "--query", 'SELECT count(*) FROM "test_table"']
    )
    for line in expected_columns:
        assert line in check_result.output


def _verify_ingest_execution_different_payloads_no_table_special_chars(runner):
    expected_columns = [
        "COLUMN_NAME      DATA_TYPE       DATA_SCALE\n",
        "---------------  ------------  ------------\n",
        "id               NUMBER\n",
        "%float_data      FLOAT\n",
        "?str_data        VARCHAR2\n",
        "@int_data        NUMBER\n",
        "^bool_data       NUMBER                   0\n",
        "&timestamp_data  TIMESTAMP(6)             6\n",
    ]

    check_result = runner.invoke(
        [
            "sql-query",
            "--query",
            "SELECT column_name, data_type, data_scale FROM user_tab_columns where table_name = 'test_table'",
        ]
    )

    for line in expected_columns:
        assert line in check_result.output

    expected_columns = ["  COUNT(*)\n", "----------\n", "         8\n"]
    check_result = runner.invoke(
        ["sql-query", "--query", 'SELECT count(*) FROM "test_table"']
    )

    for line in expected_columns:
        assert line in check_result.output


def _verify_ingest_execution_different_payloads(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
    expected = [
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  TIMESTAMP_DATA\n",
        "----  ----------  ----------  ------------  -----------  -------------------\n",
        "   0\n",
        "   1  string\n",
        "   2  string              12\n",
        "   3  string              12           1.2\n",
        "   4  string              12           1.2            1\n",
        "   5  string              12           1.2            1  2023-11-21 08:12:53\n",
        "   6  string              12           1.2\n",
        "   7  string              12           1.2            1\n",
    ]
    for row in expected:
        assert row in check_result.output


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
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
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
    check_result = runner.invoke(["sql-query", "--query", 'SELECT * FROM "test_table"'])
    expected = "a    b    c\n---  ---  ---\n  1    2    3\n"
    assert expected in check_result.output


def _verify_case_sensitive_columns(runner):
    check_result = runner.invoke(["sql-query", "--query", "SELECT * FROM TEST_TABLE"])
    print(check_result)
