# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from vdk.plugin.server import server_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_install():
    runner = CliEntryBasedTestRunner(server_plugin)

    result: Result = runner.invoke(["-v", "debug", "server", "--uninstall"])
    cli_assert_equal(0, result)

    result: Result = runner.invoke(["-v", "debug", "server", "--install"])

    cli_assert_equal(0, result)

    result: Result = runner.invoke(["-v", "debug", "server", "--status"])

    cli_assert_equal(0, result)
    assert (
        "The Versatile Data Kit Control Service is installed and running"
        in result.output
    )
