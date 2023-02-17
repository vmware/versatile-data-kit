# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.snowflake import snowflake_plugin
from vdk.plugin.snowflake.snowflake_connection import SnowflakeConnection
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


@pytest.fixture
def mocked_connection(monkeypatch):
    def mock_execute_query(*args, **kwargs):
        return [["Query successfully executed."]]

    monkeypatch.delattr(
        "vdk.plugin.snowflake.snowflake_connection.SnowflakeConnection._connect"
    )
    monkeypatch.setattr(SnowflakeConnection, "execute_query", mock_execute_query)


def test_snowflake_plugin(mocked_connection):
    """
    Test if the configuration of the Snowflake plugin
    and its general setup work as expected.
    """
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SNOWFLAKE",
            "VDK_SNOWFLAKE_ACCOUNT": "testaccount",
            "VDK_SNOWFLAKE_USER": "testuser",
            "VDK_SNOWFLAKE_PASSWORD": "testpassword",
        },
    ):
        runner = CliEntryBasedTestRunner(snowflake_plugin)

        query_result: Result = runner.invoke(
            ["snowflake-query", "--query", f"SELECT 1"]
        )

        cli_assert_equal(0, query_result)
        assert "Query successfully executed." in query_result.output
