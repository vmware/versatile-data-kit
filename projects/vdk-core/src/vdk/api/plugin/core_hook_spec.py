# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List
from typing import Optional

import click
from vdk.api.plugin.hook_markers import hookspec
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext


class CoreHookSpecs:
    """
    These are hook specifications that enable plugins to hook at core events during CLI execution.
    Those are hooks applicable for all commands (run, deploy, etc.)
    """

    @hookspec(historic=True)
    def vdk_start(
        self, plugin_registry: IPluginRegistry, command_line_args: List
    ) -> None:
        """
        Called upon immediate start of VDK just after (only) PluginRegistry is initialized.
        Nothing else (including logging, monitoring) is initialized at this point.

        :param plugin_registry: the plugin registry. Use it to register new plugin hooks
        :param command_line_args: the command arguments, can be modified.
        """
        pass

    @hookspec
    def vdk_command_line(self, root_command: click.Group) -> None:
        """
        Customize commands by adding new commands, customizing existing commands or setting default values to cli parameters

        Examples:
        Add new commands:

        .. code-block:: python
            @click.command
            def custom_command(...)
                do_something ...
            command.add_command(custom_command)

        Add options to existing commands:

        .. code-block:: python
            # note this is click.option which is a function (not the class click.Option).
            # You need to set expose_value=False if the original command method does not allow for extra arguments.
            custom_option = click.option('--custom', '-c', expose_value=False, callback = f, ...)
            # get the subcommand we want to add the option
            sub_cmd = root_command.get(None, sub_command_name)
            # replace the command with same one but now decorated with the new option
            root_command.add_command(custom_option(sub_cmd))

        Set default values to parameters:

        .. code-block:: python
            # the hookimpl decorator should have its trylast parameter set to True,
            # so that all command plugins are loaded before defaults are set

            from vdk.api.plugin.plugin_utils import set_defaults_for_specific_command, set_defaults_for_all_commands

            set_defaults_for_all_commands(root_command, {'team': 'team_name'})
            set_defaults_for_specific_command(root_command, 'command_name', {'param1': '1', 'param2': '2'})

        :param root_command: the root command which contains all sub-commands
        """

    @hookspec
    def vdk_configure(self, config_builder: "ConfigurationBuilder") -> None:
        """
        Configuring the application. Add new configuration keys and values.
        Two type of plugins can implement this hook
        * Plugin that need configuration to be provided for them later in Configuration instance and define configuration keys.
          Usually you would decorate that plugin with tryfirst=True so it's executed before all provider plugins

        * Configuration values provider plugins (e.g yaml file reader, environment vraibles configuration, etc.)
          Leave with no decorator or set trylast decorator. For such plugins it's good idea to specify configuration key
          with pattern '__config_provider__{name_of_provider}' with description that tell users on how configuration variables are updated.
          vdk config-help would print those instructions separately

        TODO: we should consider splitting this into two hooks vdk_configure_definine_vars and vdk_configure_providers

        :param config_builder:
        """
        pass

    @hookspec
    def vdk_initialize(self, context: CoreContext) -> None:
        """
        Use it to initialize the CLI or initialize modules

        :param context: The context of the current CLI execution
        """
        pass

    @hookspec
    def vdk_exception(self, exception: Exception) -> bool:
        """
        Called in case the CLI is about to exit with error.

        :return: True if exception is handled and does not need to be logged by main
        """
        pass

    @hookspec
    def vdk_exit(self, context: CoreContext, exit_code: int) -> None:
        """
        Called last just before CLI exits.

        :param context: The context of the current CLI execution
        :param exit_code: The exit code with which the CLI is about to exit.
        """
        pass


class JobRunHookSpecs:
    """
    These are hook specifications that enable plugins to hook during the run (or execution) of a Data Job.
    Generally done with "run" command of the CLI.

    They are called during as part of execution cycle of Data Job or Data Job template.
    Job template execution inherits JobContext of the job that started but all hooks are still called.
    That's because a job template is executed as a normal data job.
    """

    @hookspec
    def initialize_job(self, context: JobContext) -> None:
        """
        Called when a new job is starting to be executed. And will be use to initialize it.
        Default implementations will collect and setup list of steps to execute,
        initialize JobInput interfaces (e.g. initialize Managed databases connections)

        :param context: The Job Context of the current run.
        """
        pass

    @hookspec(firstresult=True)
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        """
        The method that executes the actual run of the data job.

        By default it executes the provided steps in context.steps one by one. It also run last (trylast is set)

        Will stop at first hook implementation that returns non-None result.
        Hence if you want to override the default implementation return a non-None result.
        If you just want to decorate it, then return None (and it's good idea to specify tryfirst=True also)

        E.g
        @hookimpl(tryfirst=True)
        create_and_run_data_job(context): # decorate with logs
            log.info(f"Start {context.name}"
            # no return

        @hookimpl
        create_and_run_data_job(context): # alternative execution algorithm
            results = run_in_parallel(steps)
            return results.all_success

        :param context: the job context
        """
        pass

    @hookspec(firstresult=True)
    def run_step(self, context: JobContext, step: Step) -> Optional[StepResult]:
        """
        Executes a step.

        The default implementation will run "runner_func" only and returns. It also run last (trylast is set)

        Will stop at first hook implementation that returns non-None result.
        Hence if you want to override the default implementation return a non-None result.
        If you just want to decorate it, then return None (and it's good idea to specify tryfirst=True also)

        :param context: the job context
        :param step: the step that will be run
        """
        pass

    @hookspec
    def finalize_job(self, context: JobContext) -> None:
        """
        Job has finished to execute.
        :param context: the job context. Use it to see the job status and the job steps statuses as well.
        """
        pass
