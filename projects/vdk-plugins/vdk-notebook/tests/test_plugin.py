import os
import pathlib
import unittest
from unittest import mock

from click.testing import Result
from vdk.plugin.notebook import notebook_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


class JupyterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(notebook_plugin, sqlite_plugin)

    def test_notebook_plugin(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "VDK_DB_DEFAULT_TYPE": "SQLITE",
                "VDK_INGEST_METHOD_DEFAULT": "sqlite",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("rest-api-test")]
            )
            cli_assert_equal(0, result)
            actual_rs: Result = self.__runner.invoke(
                ["sqlite-query", "--query", f"SELECT * FROM rest_target_table"]
            )
            cli_assert_equal(0, actual_rs)

    def test_failing_job(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "VDK_DB_DEFAULT_TYPE": "SQLITE",
                "VDK_INGEST_METHOD_DEFAULT": "sqlite",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("rest-api-test-fail")]
            )
            cli_assert_equal(1, result)