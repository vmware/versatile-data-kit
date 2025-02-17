# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_version():
    vdk_runner = CliEntryBasedTestRunner()
    result = vdk_runner.invoke(["version"])

    cli_assert_equal(0, result)
