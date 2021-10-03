# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.control_cli_plugin import vdk_plugin_control_cli
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_vdk_plugin_control_cli():
    vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli)
    result = vdk_runner.invoke(["deploy", "--help"])

    cli_assert_equal(0, result)


def test_vdk_plugin_control_cli_configuration_defined():
    vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli)
    result = vdk_runner.invoke(["config-help"])

    cli_assert_equal(0, result)
    assert (
        "CONTROL_SAMPLE_JOB_DIRECTORY" in result.output
        and "CONTROL_SERVICE_REST_API_URL" in result.output
    ), (
        "Expected to find definitions of CONTROL_SERVICE_REST_API_URL & CONTROL_SAMPLE_JOB_DIRECTORY in result output "
        f"but did not. result output is: {result.output}"
    )
