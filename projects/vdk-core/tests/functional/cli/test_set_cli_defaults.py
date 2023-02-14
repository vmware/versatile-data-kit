# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_utils import set_defaults_for_all_commands
from vdk.api.plugin.plugin_utils import set_defaults_for_specific_command
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_set_defaults_for_specific_command():
    class CommandPlugin:
        @hookimpl
        def vdk_command_line(self, root_command: click.Group):
            @click.command(name="command_test")
            @click.option(
                "-p", "--param", type=str, required=True, default="original_default"
            )
            def command_test(param):
                click.echo(param)

            root_command.add_command(command_test)

    class SetDefaultForSpecificCommandPlugin:
        @hookimpl(trylast=True)
        def vdk_command_line(self, root_command: click.Group):
            set_defaults_for_specific_command(
                root_command, "command_test", {"param": "new_default"}
            )

    runner = CliEntryBasedTestRunner(CommandPlugin())
    result: click.Result = runner.invoke(["command_test"])
    assert result.output == "original_default\n"

    runner = CliEntryBasedTestRunner(
        CommandPlugin(), SetDefaultForSpecificCommandPlugin()
    )
    result: click.Result = runner.invoke(["command_test"])
    assert result.output == "new_default\n"


def test_set_defaults_for_all_commands():
    class CommandPlugin:
        @hookimpl
        def vdk_command_line(self, root_command: click.Group):
            @click.command(name="command_test")
            @click.option(
                "-p", "--param", type=str, required=True, default="original_default"
            )
            def command_test(param):
                click.echo(param)

            root_command.add_command(command_test)

    class SetDefaultForAllCommandsPlugin:
        @hookimpl(trylast=True)
        def vdk_command_line(self, root_command: click.Group):
            set_defaults_for_all_commands(root_command, {"param": "new_default"})

    runner = CliEntryBasedTestRunner(CommandPlugin())
    result: click.Result = runner.invoke(["command_test"])
    assert result.output == "original_default\n"

    runner = CliEntryBasedTestRunner(CommandPlugin(), SetDefaultForAllCommandsPlugin())
    result: click.Result = runner.invoke(["command_test"])
    assert result.output == "new_default\n"
