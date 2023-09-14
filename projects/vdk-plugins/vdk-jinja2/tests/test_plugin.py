# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.jinja2 import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin


def test_jinja2_template():
    with mock.patch.dict(
        os.environ,
        {"VDK_DB_DEFAULT_TYPE": DB_TYPE_SQLITE_MEMORY},
    ):
        db_plugin = SqLite3MemoryDbPlugin()
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry, db_plugin)

        result: Result = runner.invoke(
            [
                "run",
                jobs_path_from_caller_directory("job-using-a-plugin"),
                "--arguments",
                '{"raw_stocks": "stocks"}',
            ]
        )

        cli_assert_equal(0, result)

        actual_agg_table_row = db_plugin.db.execute_query("select * from agg_stocks")
        assert actual_agg_table_row == [
            (20, 40, 200, 260)
        ], f"Unexpected result in aggregation table. Std Output:\n {result.output}"
