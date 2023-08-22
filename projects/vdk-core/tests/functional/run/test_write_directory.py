# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import tempfile
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_write_directory_default():
    runner = CliEntryBasedTestRunner()
    result: Result = runner.invoke(
        [
            "run",
            util.job_path("write-directory"),
            "--arguments",
            f'{{"expected_directory_string" : "{tempfile.gettempdir()}"}}',
        ]
    )
    cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {"VDK_TEMPORARY_WRITE_DIRECTORY": "TEST_VALUE_STRING"})
def test_write_directory_non_default():
    runner = CliEntryBasedTestRunner()
    result: Result = runner.invoke(
        [
            "run",
            util.job_path("write-directory"),
            "--arguments",
            '{"expected_directory_string" : "TEST_VALUE_STRING"}',
        ]
    )
    cli_assert_equal(0, result)
