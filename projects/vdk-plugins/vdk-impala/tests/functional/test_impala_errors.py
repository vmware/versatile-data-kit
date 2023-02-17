# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import pathlib
from unittest import mock

import pytest
from vdk.plugin.impala import impala_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

VDK_DB_DEFAULT_TYPE = "VDK_DB_DEFAULT_TYPE"
VDK_IMPALA_HOST = "VDK_IMPALA_HOST"
VDK_IMPALA_PORT = "VDK_IMPALA_PORT"
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


@pytest.mark.usefixtures("impala_service")
@mock.patch.dict(
    os.environ,
    {
        VDK_DB_DEFAULT_TYPE: "IMPALA",
        VDK_IMPALA_HOST: "localhost",
        VDK_IMPALA_PORT: "21050",
    },
)
class TestImpalaErrors:
    def test_impala_user_error(self, tmp_termination_msg_file):
        self.runner = CliEntryBasedTestRunner(impala_plugin)

        result = self.runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job-syntax-error")]
        )

        cli_assert_equal(1, result)
        assert (
            json.loads(tmp_termination_msg_file.read_text())["status"] == "User error"
        )
