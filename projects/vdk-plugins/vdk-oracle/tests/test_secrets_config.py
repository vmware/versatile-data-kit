# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import pytest
from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.plugin.control_cli_plugin import secrets_plugin
from vdk.plugin.control_cli_plugin import vdk_plugin_control_cli
from vdk.plugin.oracle import oracle_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Response


@pytest.fixture(scope="session")
def test_oracle_secrets_sql_only(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    secrets_data = {"vdk_user": "SYSTEM", "vdk_pass": "Gr0mh3llscr3am"}

    httpserver.expect_request(
        method="GET",
        uri=f"/data-jobs/for-team/test-team/jobs/oracle-connect-execute-job/deployments/TODO/secrets",
    ).respond_with_handler(
        lambda r: Response(status=200, response=json.dumps(secrets_data, indent=4))
    )
    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_SERVICE_REST_API_URL": api_url,
            "VDK_secrets_DEFAULT_TYPE": "control-service",
            "VDK_ORACLE_USER_SECRET": "vdk_user",
            "VDK_ORACLE_PASSWORD_SECRET": "vdk_pass",
            "VDK_ORACLE_USE_SECRETS": "True",
            "VDK_ORACLE_CONNECTION_STRING": "localhost:1521/FREE",
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_ORACLE_THICK_MODE": "False",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
            "DB_DEFAULT_TYPE": "oracle",
        },
    ):
        runner = CliEntryBasedTestRunner(
            vdk_plugin_control_cli, secrets_plugin, oracle_plugin
        )
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-connect-execute-job")]
        )
        cli_assert_equal(0, result)
    with mock.patch.dict(
        os.environ,
        {
            "VDK_ORACLE_USER": "SYSTEM",
            "VDK_ORACLE_PASSWORD": "Gr0mh3llscr3am",
            "VDK_ORACLE_USE_SECRETS": "False",
            "VDK_ORACLE_CONNECTION_STRING": "localhost:1521/FREE",
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
            "VDK_ORACLE_THICK_MODE": "False",
            "DB_DEFAULT_TYPE": "oracle",
        },
    ):
        _verify_query_execution(runner)


@pytest.fixture(scope="session")
def test_oracle_secrets_ingest_job(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    secrets_data = {"vdk_user": "SYSTEM", "vdk_pass": "Gr0mh3llscr3am"}

    httpserver.expect_request(
        method="GET",
        uri=f"/data-jobs/for-team/test-team/jobs/oracle-ingest-job/deployments/TODO/secrets",
    ).respond_with_handler(
        lambda r: Response(status=200, response=json.dumps(secrets_data, indent=4))
    )
    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_SERVICE_REST_API_URL": api_url,
            "VDK_secrets_DEFAULT_TYPE": "control-service",
            "VDK_ORACLE_USER_SECRET": "vdk_user",
            "VDK_ORACLE_PASSWORD_SECRET": "vdk_pass",
            "VDK_ORACLE_USE_SECRETS": "True",
            "VDK_ORACLE_CONNECTION_STRING": "localhost:1521/FREE",
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
            "VDK_ORACLE_THICK_MODE": "False",
            "DB_DEFAULT_TYPE": "oracle",
        },
    ):
        runner = CliEntryBasedTestRunner(
            vdk_plugin_control_cli, secrets_plugin, oracle_plugin
        )
        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("oracle-ingest-job")]
        )
        cli_assert_equal(0, result)
    with mock.patch.dict(
        os.environ,
        {
            "VDK_ORACLE_USER": "SYSTEM",
            "VDK_ORACLE_PASSWORD": "Gr0mh3llscr3am",
            "VDK_ORACLE_USE_SECRETS": "False",
            "VDK_ORACLE_CONNECTION_STRING": "localhost:1521/FREE",
            "VDK_LOG_EXECUTION_RESULT": "True",
            "VDK_INGEST_METHOD_DEFAULT": "ORACLE",
            "VDK_ORACLE_THICK_MODE": "False",
            "DB_DEFAULT_TYPE": "oracle",
        },
    ):
        _verify_ingest_execution(runner)


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
