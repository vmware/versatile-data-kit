# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock
from unittest import TestCase

import pytest
import vdk.internal.core.errors
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.greenplum import greenplum_plugin
from vdk.plugin.greenplum.ingest_to_greenplum import IngestToGreenplum
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_GREENPLUM_DBNAME = "VDK_GREENPLUM_DBNAME"
VDK_GREENPLUM_USER = "VDK_GREENPLUM_USER"
VDK_GREENPLUM_PASSWORD = "VDK_GREENPLUM_PASSWORD"
VDK_GREENPLUM_HOST = "VDK_GREENPLUM_HOST"
VDK_GREENPLUM_PORT = "VDK_GREENPLUM_PORT"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.mark.usefixtures("greenplum_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "GREENPLUM",
        VDK_GREENPLUM_DBNAME: "postgres",
        VDK_GREENPLUM_USER: "gpadmin",
        VDK_GREENPLUM_PASSWORD: "pivotal",
        VDK_GREENPLUM_HOST: "localhost",
        VDK_GREENPLUM_PORT: "5432",
        VDK_INGEST_METHOD_DEFAULT: "GREENPLUM",
    },
)
class IngestToGreenplumTests(TestCase):
    def test_ingest_to_greenplum(self):
        runner = CliEntryBasedTestRunner(greenplum_plugin)

        runner.invoke(
            [
                "greenplum-query",
                "--query",
                "CREATE TABLE test_table (some_data varchar, more_data varchar)",
            ]
        )

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_ingest_to_greenplum_job",
                ),
            ]
        )

        cli_assert_equal(0, ingest_job_result)

        check_result = runner.invoke(
            ["greenplum-query", "--query", "SELECT * FROM test_table"]
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

    def test_ingest_to_greenplum_no_dest_table(self):
        runner = CliEntryBasedTestRunner(greenplum_plugin)

        runner.invoke(["greenplum-query", "--query", "DROP TABLE IF EXISTS test_table"])

        ingest_job_result = runner.invoke(
            [
                "run",
                get_test_job_path(
                    pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
                    "test_ingest_to_greenplum_job",
                ),
            ]
        )

        assert 'relation "test_table" does not exist' in ingest_job_result.output
