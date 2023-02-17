# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest import mock

from click.testing import Result
from vdk.plugin.notebook import notebook_plugin
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@mock.patch.dict(
    os.environ,
    {
        "VDK_DB_DEFAULT_TYPE": "SQLITE",
        "VDK_INGEST_METHOD_DEFAULT": "sqlite",
    },
)
class JupyterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(notebook_plugin, sqlite_plugin)

    def test_successful_job(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("rest-api-job")]
        )
        cli_assert_equal(0, result)
        actual_rs: Result = self.__runner.invoke(
            ["sqlite-query", "--query", "SELECT * FROM rest_target_table"]
        )
        assert actual_rs.stdout == (
            "  userId    id  title                 completed\n"
            "--------  ----  ------------------  -----------\n"
            "       1     1  delectus aut autem            0\n"
        )

    def test_failing_job_with_syntax_error(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("rest-api-job-fail-syntax-error")]
        )
        cli_assert_equal(1, result)

    def test_failing_job_with_code_error(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("rest-api-job-fail-code-error")]
        )
        cli_assert_equal(2, result)

    def test_failing_job_with_sql_error(self) -> None:
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("rest-api-job-sql-error")]
        )
        cli_assert_equal(1, result)
