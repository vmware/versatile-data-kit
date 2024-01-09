# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock
from unittest import TestCase

import pytest
from vdk.plugin.postgres import postgres_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_POSTGRES_DBNAME = "VDK_POSTGRES_DBNAME"
VDK_POSTGRES_USER = "VDK_POSTGRES_USER"
VDK_POSTGRES_PASSWORD = "VDK_POSTGRES_PASSWORD"
VDK_POSTGRES_HOST = "VDK_POSTGRES_HOST"
VDK_POSTGRES_PORT = "VDK_POSTGRES_PORT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.mark.usefixtures("postgres_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "POSTGRES",
        VDK_POSTGRES_DBNAME: "postgres",
        VDK_POSTGRES_USER: "postgres",
        VDK_POSTGRES_PASSWORD: "postgres",
        VDK_POSTGRES_HOST: "localhost",
        VDK_POSTGRES_PORT: "5432",
        VDK_INGEST_METHOD_DEFAULT: "POSTGRES",
    },
)
class IngestToPostgresTests(TestCase):
    def test_ingest_to_postgres(self):
        runner = CliEntryBasedTestRunner(postgres_plugin)

        query_result = runner.invoke(
            [
                "postgres-query",
                "--query",
                "CREATE TABLE test_table "
                "(some_data varchar, more_data varchar, int_data bigint, float_data real, bool_data boolean)",
            ]
        )
        cli_assert_equal(0, query_result)

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test-ingest",
                ),
            ]
        )

        cli_assert_equal(0, ingest_job_result)

        check_result = runner.invoke(
            ["postgres-query", "--query", "SELECT * FROM test_table"]
        )

        assert check_result.stdout == (
            "--------------  --------------  --  ----  ----\n"
            "some_test_data  more_test_data  11  3.14  True\n"
            "some_test_data  more_test_data  11  3.14  True\n"
            "some_test_data  more_test_data  11  3.14  True\n"
            "some_test_data  more_test_data  11  3.14  True\n"
            "some_test_data  more_test_data  11  3.14  True\n"
            "--------------  --------------  --  ----  ----\n"
        )

    def test_ingest_no_dest_table(self):
        runner = CliEntryBasedTestRunner(postgres_plugin)

        query_result = runner.invoke(
            ["postgres-query", "--query", "DROP TABLE IF EXISTS test_table"]
        )
        cli_assert_equal(0, query_result)

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test-ingest",
                ),
            ]
        )

        assert 'relation "test_table" does not exist' in ingest_job_result.output
