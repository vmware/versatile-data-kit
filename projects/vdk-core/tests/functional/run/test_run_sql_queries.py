# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import sqlite3
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.internal.core.errors import VdkConfigurationError
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import DecoratedSqLite3MemoryDbPlugin
from vdk.plugin.test_utils.util_plugins import SqLite3MemoryDbPlugin

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection_no_such_db_type():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(
        [
            "run",
            util.job_path("simple-create-insert"),
        ]
    )

    cli_assert_equal(1, result)
    assert isinstance(result.exception, VdkConfigurationError)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_dbapi_connection():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert",
            ),
        ]
    )

    cli_assert_equal(0, result)


# TODO: enable after managed cursor merge
# @mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
# def test_run_managed_connection_and_check_query_comments():
#     db_plugin = DecoratedSqLite3MemoryDbPlugin()
#     runner = CliEntryBasedTestRunner(db_plugin)
#
#     result: Result = runner.invoke(
#         [
#             "run",
#             get_test_job_path(
#                 pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
#                 "simple-create-insert",
#             ),
#         ]
#     )
#
#     cli_assert_equal(0, result)
#     assert len(db_plugin.statements_history) == 3
#     # assert those are automatically added as comments
#     assert all(
#         ["-- op_id" in statement for statement in db_plugin.statements_history]
#     ), f"op_id missing: {db_plugin.statements_history}"
#     assert all(
#         ["-- job_name" in statement for statement in db_plugin.statements_history]
#     ), f"job name missing: {db_plugin.statements_history}"


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_managed_connection_and_query_fails():
    db_plugin = DecoratedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "simple-create-insert-failed",
            ),
        ]
    )

    cli_assert_equal(1, result)
    assert isinstance(result.exception, sqlite3.OperationalError)


@mock.patch.dict(os.environ, {VDK_DB_DEFAULT_TYPE: DB_TYPE_SQLITE_MEMORY})
def test_run_job_with_arguments():
    db_plugin = SqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    result: Result = runner.invoke(
        [
            "run",
            get_test_job_path(
                pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                "job-with-args",
            ),
            "--arguments",
            '{"table_name": "test_table", "counter": 123}',
        ]
    )

    cli_assert_equal(0, result)
    assert db_plugin.db.execute_query("select * from test_table") == [("one", 123)]
