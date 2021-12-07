# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import time
import unittest
from unittest.mock import patch

import pytest
from click.testing import Result
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"


@pytest.mark.usefixtures("impala_service")
@patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "IMPALA",
        VDK_IMPALA_HOST: "localhost",
        VDK_IMPALA_PORT: "21050",
    },
)
class ImpalaConnectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(impala_plugin)

    def test_execute_query(self) -> None:
        time.sleep(10)
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        actual_rs: Result = self.__runner.invoke(
            ["impala-query", "--query", "SELECT * FROM stocks"]
        )
        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output
