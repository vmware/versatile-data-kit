# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.sql_extensions import plugin_entry
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

"""
This is a sample test file showing a recommended way to test new plugins.
A good way to test a new plugin is how it would be used in the command that it extends.
"""


def test_sql_splitter_plugin():
    with mock.patch.dict(
        os.environ,
        {"DB_DEFAULT_TYPE": "sqlite"},
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry, sqlite_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )
        cli_assert_equal(0, result)
