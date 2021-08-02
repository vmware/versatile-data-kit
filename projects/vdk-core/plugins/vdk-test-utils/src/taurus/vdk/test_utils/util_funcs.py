# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import traceback
from typing import cast
from typing import Optional

import click
from click.testing import CliRunner
from click.testing import Result
from taurus.api.plugin.core_hook_spec import CoreHookSpecs
from taurus.api.plugin.core_hook_spec import JobRunHookSpecs
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk import cli_entry
from taurus.vdk.builtin_plugins.internal_hookspecs import InternalHookSpecs
from taurus.vdk.builtin_plugins.run.data_job import DataJob
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.builtin_plugins.run.step import Step
from taurus.vdk.builtin_plugins.run.step import StepBuilder
from taurus.vdk.builtin_plugins.run.step import StepFunction
from taurus.vdk.cli_entry import CliEntry
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import StateStore
from taurus.vdk.plugin.plugin import PluginRegistry
from taurus.vdk.test_utils.util_plugins import TestPropertiesPlugin


def cli_assert(is_true, result: Result) -> None:
    assert is_true, (
        f"result assert fails, Output: {result.output} "
        f"Exception:\n {''.join(traceback.format_exception(*result.exc_info))} "
    )


def cli_assert_equal(expected_exit_code, result: Result) -> None:
    assert result.exit_code == expected_exit_code, (
        f"result exit code is not {expected_exit_code} but it is {result.exit_code}, \n"
        f"Exception:\n {''.join(traceback.format_exception(*result.exc_info))} \n"
        f"Output:\n {result.output}"
    )


class TestingCliEntryPlugin:
    def __init__(self, runner=CliRunner(), **extra):
        """
        :param runner: the CLI test runner.
        """
        self.runner = runner
        self.extra = extra
        self.result: Optional[Result] = None

    @hookimpl(tryfirst=True)
    def vdk_cli_execute(
        self,
        root_command: click.Command,
        command_line_args: list,
        program_name: str,
        core_context: CoreContext,
    ) -> int:
        self.result = self.runner.invoke(
            cli=root_command,
            args=command_line_args,
            obj=core_context,
            prog_name=program_name,
            **self.extra,
        )
        return self.result.exit_code


class CliEntryBasedTestRunner:
    """
    Enables to run CLI commands for unit testing purposes in a isolated environment.
    It relies on click.testing.CliRunner and simply setups plugin registry and
    replaces normal cli calls with those with CliRunner.

    """

    def __init__(self, *plugins):
        """
        :param plugins: the list of plugins that should be loaded during this test run.
        """
        self._plugins = plugins
        self._default_plugins = [TestPropertiesPlugin()]

    def clear_default_plugins(self):
        self._default_plugins.clear()

    def invoke(self, args, cli=cli_entry.cli, **extra) -> Result:
        plugin_registry = PluginRegistry()
        plugin_registry.add_hook_specs(InternalHookSpecs)
        plugin_registry.load_plugin_with_hooks_impl(CliEntry(), "cli-entry")

        testing_cli_entry = TestingCliEntryPlugin(**extra)
        plugin_registry.load_plugin_with_hooks_impl(
            testing_cli_entry, "testing-cli-entry"
        )
        for plugin in self._default_plugins:
            plugin_registry.load_plugin_with_hooks_impl(plugin)
        for plugin in self._plugins:
            plugin_registry.load_plugin_with_hooks_impl(plugin)

        exit_code = cast(InternalHookSpecs, plugin_registry.hook()).vdk_main(
            plugin_registry=plugin_registry, root_command=cli, command_line_args=args
        )
        testing_cli_entry.result.exit_code = exit_code
        return testing_cli_entry.result


def get_test_job_path(current_dir: pathlib.Path, job_name: str) -> str:
    """Get the path of the test data job returned as string so it can be passed easier as cmd line args"""
    jobs_dir = current_dir.joinpath("jobs")
    return str(jobs_dir.joinpath(job_name))


def jobs_path_from_caller_directory(job_name: str):
    """
    Get data job path by looking at "jobs" directory. "jobs" directory is search in same one as caller's file directory.
    """
    import inspect

    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    caller_dir = pathlib.Path(os.path.dirname(os.path.abspath(module.__file__)))
    return get_test_job_path(caller_dir, job_name)


class DataJobBuilder:
    def __init__(self):
        self.step_builder: StepBuilder = StepBuilder()
        self.core_context = self.__get_core_context()
        self.name = "test-job"

    def __get_core_context(self):
        core_context = CoreContext(
            PluginRegistry(), ConfigurationBuilder().build(), StateStore()
        )
        core_context.plugin_registry.add_hook_specs(CoreHookSpecs)
        core_context.plugin_registry.add_hook_specs(JobRunHookSpecs)
        core_context.plugin_registry.load_plugin_with_hooks_impl(
            self, "test-job-builder"
        )
        return core_context

    @hookimpl(trylast=True)
    def initialize_job(self, context: JobContext) -> None:
        context.step_builder = self.step_builder

    def add_step_func(
        self, step_runner_func: StepFunction, step_name="test", step_type="test"
    ) -> None:
        self.step_builder.add_step(
            Step(
                name=step_name,
                type=step_type,
                runner_func=step_runner_func,
                file_path=pathlib.Path(__file__),
                job_dir=pathlib.Path(__file__),
            )
        )

    def build(self) -> DataJob:
        return DataJob(None, self.core_context, name=self.name)
