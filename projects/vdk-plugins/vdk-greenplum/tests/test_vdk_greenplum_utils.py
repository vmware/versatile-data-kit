# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.greenplum import greenplum_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_GREENPLUM_DBNAME = "VDK_GREENPLUM_DBNAME"
VDK_GREENPLUM_USER = "VDK_GREENPLUM_USER"
VDK_GREENPLUM_PASSWORD = "VDK_GREENPLUM_PASSWORD"
VDK_GREENPLUM_HOST = "VDK_GREENPLUM_HOST"
VDK_GREENPLUM_PORT = "VDK_GREENPLUM_PORT"


@pytest.mark.usefixtures("greenplum_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "GREENPLUM",
        VDK_GREENPLUM_DBNAME: "postgres",
        VDK_GREENPLUM_USER: "gpadmin",
        VDK_GREENPLUM_PASSWORD: "pivotal",
        VDK_GREENPLUM_HOST: "localhost",
        VDK_GREENPLUM_PORT: "5432",
    },
)
class GreenplumUtilsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(greenplum_plugin)

    def test_execute_query(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        actual_rs: Result = self.__runner.invoke(
            ["greenplum-query", "--query", "SELECT * FROM stocks"]
        )
        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output
