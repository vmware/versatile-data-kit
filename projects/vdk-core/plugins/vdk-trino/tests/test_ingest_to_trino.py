# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock
from unittest import TestCase

import pytest
import vdk.internal.core.errors
from vdk.internal import trino_plugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.errors import UserCodeError
from vdk.internal.ingest_to_trino import IngestToTrino
from vdk.internal.test_utils.util_funcs import cli_assert_equal
from vdk.internal.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.internal.test_utils.util_funcs import get_test_job_path

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.mark.usefixtures("trino_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "TRINO",
        VDK_TRINO_PORT: "8080",
        VDK_TRINO_USE_SSL: "False",
        VDK_INGEST_METHOD_DEFAULT: "TRINO",
    },
)
class IngestToTrinoTests(TestCase):
    def test_ingest_to_trino(self):
        runner = CliEntryBasedTestRunner(trino_plugin)

        runner.invoke(
            [
                "trino-query",
                "--query",
                "CREATE TABLE IF NOT EXISTS test_table (some_data varchar, more_data varchar)",
            ]
        )

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_ingest_to_trino_job",
                ),
            ]
        )

        cli_assert_equal(0, ingest_job_result)

        check_result = runner.invoke(
            ["trino-query", "--query", "SELECT * FROM test_table"]
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

    def test_ingest_to_trino_no_dest_table(self):
        runner = CliEntryBasedTestRunner(trino_plugin)

        runner.invoke(["trino-query", "--query", "DROP TABLE IF EXISTS test_table"])

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_ingest_to_trino_job",
                ),
            ]
        )

        assert "TABLE_NOT_FOUND" in ingest_job_result.output
