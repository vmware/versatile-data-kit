# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.postgres import postgres_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_POSTGRES_DBNAME = "VDK_POSTGRES_DBNAME"
VDK_POSTGRES_USER = "VDK_POSTGRES_USER"
VDK_POSTGRES_PASSWORD = "VDK_POSTGRES_PASSWORD"
VDK_POSTGRES_HOST = "VDK_POSTGRES_HOST"
VDK_POSTGRES_PORT = "VDK_POSTGRES_PORT"


@pytest.mark.usefixtures("postgres_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "POSTGRES",
        VDK_POSTGRES_DBNAME: "postgres",
        VDK_POSTGRES_USER: "postgres",
        VDK_POSTGRES_PASSWORD: "postgres",
        VDK_POSTGRES_HOST: "localhost",
        VDK_POSTGRES_PORT: "5432",
    },
)
class PostgresUtilsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(postgres_plugin)

    def test_execute_query(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        actual_rs: Result = self.__runner.invoke(
            ["postgres-query", "--query", "SELECT * FROM stocks"]
        )
        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output
