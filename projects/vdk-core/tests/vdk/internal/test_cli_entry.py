# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from click.testing import CliRunner
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.cli_entry import cli
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"


def test_main():
    @click.command("my-echo")
    @click.argument("value")
    def my_echo(value):
        click.echo(value)

    class AddEchoCmdPlugin:
        @hookimpl(tryfirst=True)
        def vdk_command_line(self, root_command: click.Group) -> None:
            root_command.add_command(my_echo)

    vdk_runner = CliEntryBasedTestRunner(AddEchoCmdPlugin())
    result = vdk_runner.invoke(["my-echo", "hi"])

    cli_assert_equal(0, result)
    assert str(result.output).strip() == "hi"
