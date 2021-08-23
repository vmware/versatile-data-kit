# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from taurus.vdk import sqlite_plugin
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner
from taurus.vdk.test_utils.util_funcs import jobs_path_from_caller_directory


def test_sqlite_plugin(tmpdir):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )

        cli_assert_equal(0, result)

        actual_rs: Result = runner.invoke(
            ["sqlite-query", "--query", f"SELECT * FROM stocks"]
        )

        cli_assert_equal(0, actual_rs)
        assert "GOOG" in actual_rs.output
