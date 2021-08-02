# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
from typing import cast
from typing import List

import click
import click_log
from click import ClickException
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from taurus.api.plugin.core_hook_spec import CoreHookSpecs
from taurus.api.plugin.hook_markers import hookimpl
from taurus.api.plugin.plugin_registry import IPluginRegistry
from taurus.vdk.builtin_plugins import builtin_hook_impl
from taurus.vdk.builtin_plugins.internal_hookspecs import InternalHookSpecs
from taurus.vdk.core.config import Configuration
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import StateStore
from taurus.vdk.plugin.plugin import PluginRegistry

log = logging.getLogger(__name__)


# TODO: perhaps we do not need click-plugins and we can use vdk_initialize hook (and cli.add_command)
@with_plugins(iter_entry_points("vdk.plugin.cli"))
@click.group(
    help="""Command line tool for Data Jobs management.

The cli enables you to conveniently create, develop, run, deploy, list and manage Data Jobs.

\b
# Run to see list of available commands
vdk --help

\b
# Show help of run command (can be done for each command)
vdk run --help

"""
)
@click_log.simple_verbosity_option(logging.getLogger())
@click.pass_context
def cli(ctx: click.Context) -> int:
    """
    Method used to declare root CLI command through decorators.
    """
    return 0


def build_configuration(plugin_registry) -> Configuration:
    """
    We are calling vdk_configure hook and building Configuration of the CLI.
    """
    log.debug("Configure ...")
    conf_builder = ConfigurationBuilder()
    cast(CoreHookSpecs, plugin_registry.hook()).vdk_configure(
        config_builder=conf_builder
    )
    configuration = conf_builder.build()
    return configuration


def setup_cli_commands(plugin_registry: IPluginRegistry, root_command: click.Group):
    """
    Call hooks to customize CLI Commands
    """
    log.debug("Setup commands and options ...")
    cast(CoreHookSpecs, plugin_registry.hook()).vdk_command_line(
        root_command=root_command
    )


def build_core_context_and_initialize(
    configuration: Configuration, plugin_registry: IPluginRegistry
) -> CoreContext:
    core_context = CoreContext(plugin_registry, configuration, StateStore())
    log.debug("Initialize ...")
    cast(CoreHookSpecs, plugin_registry.hook()).vdk_initialize(context=core_context)
    return core_context


class CliEntry:
    @hookimpl(trylast=True)
    def vdk_cli_execute(
        self,
        root_command: click.Command,
        command_line_args: List,
        program_name: str,
        core_context: CoreContext,
    ) -> int:
        # arguments passed are propagated to click.core.main
        exit_code = root_command(
            args=command_line_args,
            prog_name=program_name,
            complete_var=None,
            standalone_mode=True,
            obj=core_context,
        )
        return exit_code

    @hookimpl(trylast=True)
    def vdk_main(
        self,
        plugin_registry: IPluginRegistry,
        root_command: click.Group,
        command_line_args: List,
    ) -> int:
        """
        Main method of the CLI. It call all configuration and initialization hooks and start CLI
        """

        plugin_registry.add_hook_specs(CoreHookSpecs)
        plugin_registry.load_plugin_with_hooks_impl(builtin_hook_impl, "core-plugin")

        program_name = "vdk"  # TODO: infer
        plugin_registry.hook().vdk_start.call_historic(
            kwargs=dict(
                plugin_registry=plugin_registry, command_line_args=command_line_args
            )
        )

        setup_cli_commands(plugin_registry, root_command)
        configuration = build_configuration(plugin_registry)
        core_context = build_core_context_and_initialize(configuration, plugin_registry)

        exit_code = 0
        try:
            log.info(f"Start CLI {program_name} with args {command_line_args}")
            exit_code = cast(InternalHookSpecs, plugin_registry.hook()).vdk_cli_execute(
                root_command=root_command,
                command_line_args=command_line_args,
                core_context=core_context,
                program_name=program_name,
            )
            return exit_code
        except Exception as e:
            handled = cast(CoreHookSpecs, plugin_registry.hook()).vdk_exception(
                exception=e
            )
            # if at least one hook implementation returned handled, means we do not need to log the exception
            if not (True in handled):
                log.exception("Exiting with exception.")
            exit_code = e.exit_code if isinstance(e, ClickException) else 1
            return exit_code
        finally:
            cast(CoreHookSpecs, plugin_registry.hook()).vdk_exit(
                context=core_context, exit_code=exit_code
            )


def main() -> None:
    """
    This the starting point for the Python vdk console script.
    """
    # configure basic logging , it's expected that a plugin would override and set it up properly
    click_log.basic_config(logging.getLogger())

    log.debug("Setup plugin registry and call vdk_start hooks ...")
    plugin_registry = PluginRegistry()
    plugin_registry.add_hook_specs(InternalHookSpecs)
    plugin_registry.load_plugins_from_setuptools_entrypoints()
    plugin_registry.load_plugin_with_hooks_impl(CliEntry(), "cli-entry")

    exit_code = cast(InternalHookSpecs, plugin_registry.hook()).vdk_main(
        plugin_registry=plugin_registry,
        root_command=cli,
        command_line_args=sys.argv[1:],
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
