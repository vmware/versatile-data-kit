# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest import mock

from click.testing import Result
from vdk.plugin.jupyter import jupyter_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


class JupyterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(jupyter_plugin, sqlite_plugin)

    def test_jupyter_plugin(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "VDK_DB_DEFAULT_TYPE": "SQLITE",
                "VDK_INGEST_METHOD_DEFAULT": "sqlite",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("jupyter-job")]
            )
            cli_assert_equal(0, result)
            actual_rs: Result = self.__runner.invoke(
                ["sqlite-query", "--query", f"SELECT * FROM rest_target_table"]
            )
            cli_assert_equal(0, actual_rs)

    def test_no_step_job(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("no-step-job")]
        )
        cli_assert_equal(1, result)
