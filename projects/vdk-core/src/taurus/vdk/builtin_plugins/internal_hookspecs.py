# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

import click
from taurus.api.plugin.hook_markers import hookspec
from taurus.api.plugin.plugin_registry import IPluginRegistry
from taurus.vdk.core.context import CoreContext


class InternalHookSpecs:
    """
    These are the hook specs that are used in internal implementation or testing of vdk-core.
    And we are not considering them useful and impactful enough to be made public.
    """

    @hookspec(firstresult=True)
    def vdk_main(
        self,
        plugin_registry: IPluginRegistry,
        root_command: click.Group,
        command_line_args: List,
    ) -> int:
        """
        Called for running the main mltethod of the CLI.
        Default implementation does register hook specs and implementations, initialize the CLI and executes it.

        :param plugin_registry: the Plugin Registry which can be used to add hook specs or implementations
        :param root_command: the root CLI command
        :param command_line_args: the command line args
        :return: the exit code. Immediately after that sys.exit(exit_code) is called.
        """
        pass

    @hookspec(firstresult=True)
    def vdk_cli_execute(
        self,
        root_command: click.Command,
        command_line_args: List,
        program_name: str,
        core_context: CoreContext,
    ) -> int:
        """

        :param root_command: the (root) click command that will be executed and run the application
        :param command_line_args: the arguments with which it is started
        :param program_name: the name of the program.
        :param core_context: the initialized core context of the CLI
        :return: the exit code with which the CLI execution finishes
        In case of error it may also throw an exception
        """
