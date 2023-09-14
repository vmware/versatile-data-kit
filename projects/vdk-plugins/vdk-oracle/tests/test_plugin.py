# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.oracle import oracle_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.fixture(scope="session", autouse=True)
def configure_oracle_environment():
    with mock.patch.dict(
        os.environ,
        {
            "DB_DEFAULT_TYPE": "oracle",
            "ORACLE_USER": "admin",
            "ORACLE_PASSWORD": "Gr0mh3llscr3am",
            "ORACLE_CONNECTION_STRING": "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=ge975b87ba26804_ndb_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))",
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
        },
    ) as _fixture:
        yield _fixture


def test_oracle_connect_execute():
    runner = CliEntryBasedTestRunner(oracle_plugin)
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
    )
    cli_assert_equal(0, result)
    _verify_query_execution(runner)


def test_oracle_ingest_existing_table():
    runner = CliEntryBasedTestRunner(oracle_plugin)
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("oracle-ingest-job")]
    )
    cli_assert_equal(0, result)
    _verify_ingest_execution(runner)


def test_oracle_ingest_no_table():
    runner = CliEntryBasedTestRunner(oracle_plugin)
    result: Result = runner.invoke(
        ["run", jobs_path_from_caller_directory("oracle-ingest-job-no-table")]
    )
    cli_assert_equal(0, result)
    _verify_ingest_execution_no_table(runner)


def test_oracle_ingest_different_payloads():
    runner = CliEntryBasedTestRunner(oracle_plugin)
    result: Result = runner.invoke(
        [
            "run",
            jobs_path_from_caller_directory("oracle-ingest-job-different-payloads"),
        ]
    )
    cli_assert_equal(0, result)
    _verify_ingest_execution_different_payloads(runner)


def test_oracle_ingest_different_payloads_no_table():
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


def test_oracle_ingest_blob():
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
        "10:12:53             0.1\n"
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
        "2023-11-21T10:12:53             1.1\n"
        "   1  string              12           1.2            1  "
        "2023-11-21T10:12:53             1.1\n"
        "   2  string              12           1.2            1  "
        "2023-11-21T10:12:53             1.1\n"
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
        "10:12:53\n"
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
