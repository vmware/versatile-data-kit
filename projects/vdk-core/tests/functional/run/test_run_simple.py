# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_run():
    runner = CliEntryBasedTestRunner()

    result: Result = runner.invoke(["run", util.job_path("simple-job")])

    cli_assert_equal(0, result)
