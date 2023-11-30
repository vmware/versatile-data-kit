# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
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
VDK_LOG_EXECUTION_RESULT = "VDK_LOG_EXECUTION_RESULT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.mark.usefixtures("oracle_db")
@mock.patch.dict(
    os.environ,
    {
        DB_DEFAULT_TYPE: "oracle",
        ORACLE_USER: "SYSTEM",
        ORACLE_PASSWORD: "Gr0mh3llscr3am",
        ORACLE_CONNECTION_STRING: "localhost:1521/FREE",
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

    def test_oracle_ingest_existing_table(self):
        runner = CliEntryBasedTestRunner(oracle_plugin)
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job")]
        )
        cli_assert_equal(0, result)
        _verify_ingest_execution(runner)

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


def _verify_query_execution(runner):
    check_result = runner.invoke(["oracle-query", "--query", "SELECT * FROM todoitem"])
    expected = (
        "  ID  DESCRIPTION      DONE\n"
        "----  -------------  ------\n"
        "   1  Task 1              1\n"
    )
    assert check_result.output == expected


def _verify_ingest_execution(runner):
    check_result = runner.invoke(
        ["oracle-query", "--query", "SELECT * FROM test_table"]
    )
    expected = (
        "  ID  STR_DATA      INT_DATA    FLOAT_DATA    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  ------------  -----------  "
        "-------------------  --------------\n"
        "   5  string              12           1.2            1  2023-11-21 "
        "08:12:53             0.1\n"
    )
    assert check_result.output == expected


def _verify_ingest_execution_type_inference(runner):
    check_result = runner.invoke(
        ["oracle-query", "--query", "SELECT * FROM test_table"]
    )
    expected = (
        "  ID  STR_DATA      INT_DATA  NAN_INT_DATA      FLOAT_DATA    BOOL_DATA  "
        "TIMESTAMP_DATA         DECIMAL_DATA\n"
        "----  ----------  ----------  --------------  ------------  -----------  "
        "-------------------  --------------\n"
        "   5  string              12                           1.2            1  "
        "2023-11-21 08:12:53             0.1\n"
    )
    assert check_result.output == expected


def _verify_ingest_execution_no_table(runner):
    check_result = runner.invoke(
        ["oracle-query", "--query", "SELECT * FROM test_table"]
    )
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
    assert check_result.output == expected


def _verify_ingest_execution_different_payloads_no_table(runner):
    check_result = runner.invoke(
        ["oracle-query", "--query", "SELECT count(*) FROM test_table"]
    )
    expected = "  COUNT(*)\n----------\n         8\n"
    assert check_result.output == expected


def _verify_ingest_execution_different_payloads(runner):
    check_result = runner.invoke(
        ["oracle-query", "--query", "SELECT * FROM test_table"]
    )
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
    assert check_result.output == expected


def _verify_ingest_blob(runner):
    check_result = runner.invoke(
        [
            "oracle-query",
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
    assert check_result.output == expected
