# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

import py
from click.testing import CliRunner
from click.testing import Result
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"


def test_execute_sql(tmpdir: py.path.local):
    with mock.patch.dict(
        os.environ,
        {
            VDK_DB_DEFAULT_TYPE: "sqlite",
            "SQLITE_FILE": os.path.join(str(tmpdir), "sqlite-tmp"),
        },
    ):
        runner = CliEntryBasedTestRunner()

        result: Result = runner.invoke(
            [
                "sql-query",
                "--query",
                "CREATE TABLE cli_stocks (date text, symbol text, price real)",
            ]
        )
        cli_assert_equal(0, result)

        result: Result = runner.invoke(
            [
                "sql-query",
                "--query",
                """
                INSERT INTO cli_stocks VALUES ('2020-01-01', 'GOOG', 123.0), ('2020-01-01', 'GOOG', 123.0)
                """,
            ]
        )
        cli_assert_equal(0, result)

        result: Result = runner.invoke(
            ["sql-query", "--query", "select * from cli_stocks"],
            runner=CliRunner(
                mix_stderr=False
            ),  # TODO: replace when CliEntryBasedTestRunner add support for it
        )
        cli_assert_equal(0, result)
        expected_stdout = (
            "date        symbol      price\n"
            "----------  --------  -------\n"
            "2020-01-01  GOOG          123\n"
            "2020-01-01  GOOG          123\n"
        )
        assert expected_stdout == result.stdout

        result: Result = runner.invoke(
            ["sql-query", "--output", "json", "--query", "select * from cli_stocks"],
            runner=CliRunner(
                mix_stderr=False
            ),  # TODO: replace when CliEntryBasedTestRunner add support for it
        )
        cli_assert_equal(0, result)
        expected_stdout_json = [
            {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
            {"date": "2020-01-01", "symbol": "GOOG", "price": 123.0},
        ]
        assert expected_stdout_json == json.loads(result.stdout)
