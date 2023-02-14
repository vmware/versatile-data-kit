# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest.mock import call
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
VDK_IMPALA_SYNC_DDL = "VDK_IMPALA_SYNC_DDL"
VDK_IMPALA_QUERY_POOL = "VDK_IMPALA_QUERY_POOL"


@pytest.mark.usefixtures("impala_service")
class ImpalaConnectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(impala_plugin)

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
        },
    )
    def test_execute_query(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        actual_rs: Result = self.__runner.invoke(
            ["impala-query", "--query", "SELECT * FROM stocks"]
        )
        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output

    @patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "IMPALA",
            VDK_IMPALA_HOST: "localhost",
            VDK_IMPALA_PORT: "21050",
            VDK_IMPALA_SYNC_DDL: "True",
            VDK_IMPALA_QUERY_POOL: "testing_grounds",
        },
    )
    @patch("vdk.plugin.impala.impala_plugin.DecorationCursor.execute")
    def test_execute_query_with_sync_ddl_and_query_pool(self, mock_dc_execute) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)

        assert call("SET SYNC_DDL=True") in mock_dc_execute.call_args_list
        assert (
            call("SET REQUEST_POOL='testing_grounds'") in mock_dc_execute.call_args_list
        )
