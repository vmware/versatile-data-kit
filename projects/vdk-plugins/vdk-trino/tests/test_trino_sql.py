# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from unittest import mock

import pytest
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
from vdk.plugin.trino import trino_plugin

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_TRINO_PORT = "VDK_TRINO_PORT"
VDK_TRINO_USE_SSL = "VDK_TRINO_USE_SSL"
VDK_INGEST_METHOD_DEFAULT = "VDK_INGEST_METHOD_DEFAULT"


@pytest.fixture(autouse=True)
def tmp_termination_msg_file(tmpdir) -> pathlib.Path:
    out_file = str(tmpdir.join("termination-log"))
    with mock.patch.dict(
        os.environ,
        {
            "VDK_TERMINATION_MESSAGE_WRITER_ENABLED": "true",
            "VDK_TERMINATION_MESSAGE_WRITER_OUTPUT_FILE": out_file,
        },
    ):
        yield pathlib.Path(out_file)


def _job_path(job_name: str) -> str:
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))),
        job_name,
    )


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
class TestTrinoSql:
    def test_sql(self):
        runner = CliEntryBasedTestRunner(trino_plugin)

        result = runner.invoke(
            [
                "run",
                _job_path("sql-job"),
            ]
        )

        cli_assert_equal(0, result)

        check_result = runner.invoke(
            ["trino-query", "--query", "SELECT * FROM sql_job_table"]
        )

        assert check_result.stdout == "---\n" "111\n" "---\n"

    def test_sql_user_error(self, tmp_termination_msg_file):
        runner = CliEntryBasedTestRunner(trino_plugin)

        result = runner.invoke(["run", _job_path("sql-job-syntax-error")])

        cli_assert_equal(1, result)
        assert (
            json.loads(tmp_termination_msg_file.read_text())["status"] == "User error"
        )

    @mock.patch.dict(
        os.environ,
        {
            VDK_TRINO_PORT: "9398",
        },
    )
    def test_sql_connectivity_error(self, tmp_termination_msg_file):
        runner = CliEntryBasedTestRunner(trino_plugin)

        result = runner.invoke(["run", _job_path("sql-job")])

        cli_assert_equal(1, result)
        assert (
            json.loads(tmp_termination_msg_file.read_text())["status"] == "User error"
        )
