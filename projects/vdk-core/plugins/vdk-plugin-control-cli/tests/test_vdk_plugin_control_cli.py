# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.vdk import vdk_plugin_control_cli
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner


def test_vdk_plugin_control_cli():
    vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli)
    result = vdk_runner.invoke(["deploy", "--help"])

    cli_assert_equal(0, result)
