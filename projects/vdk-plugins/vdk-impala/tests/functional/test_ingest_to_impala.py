# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import TestCase
from unittest.mock import patch

import pytest
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.mark.usefixtures("impala_service")
@patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "IMPALA",
        VDK_IMPALA_HOST: "localhost",
        VDK_IMPALA_PORT: "21050",
        VDK_INGEST_METHOD_DEFAULT: "IMPALA",
    },
)
class IngestToImpalaTests(TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(impala_plugin)

    def test_ingest_to_impala(self):
        self.__runner.invoke(
            [
                "impala-query",
                "--query",
                "CREATE TABLE test_table (some_data varchar, more_data varchar)",
            ]
        )

        ingest_job_result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "ingest-job",
                ),
            ]
        )

        cli_assert_equal(0, ingest_job_result)

        check_result = self.__runner.invoke(
            ["impala-query", "--query", "SELECT * FROM test_table"]
        )

        assert check_result.stdout == (
            "--------------  --------------\n"
            "some_test_data  more_test_data\n"
            "some_test_data  more_test_data\n"
            "some_test_data  more_test_data\n"
            "some_test_data  more_test_data\n"
            "some_test_data  more_test_data\n"
            "--------------  --------------\n"
        )

    def test_ingest_to_impala_no_dest_table(self):
        self.__runner.invoke(
            ["impala-query", "--query", "DROP TABLE IF EXISTS test_table"]
        )

        ingest_job_result = self.__runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "ingest-job",
                ),
            ]
        )

        assert "Table does not exist" in ingest_job_result.output
