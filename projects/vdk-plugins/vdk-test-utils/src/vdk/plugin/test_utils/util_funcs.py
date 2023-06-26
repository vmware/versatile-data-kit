# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import traceback
from typing import cast
from typing import Optional
from unittest.mock import MagicMock

import click
from click.testing import CliRunner
from click.testing import Result
from vdk.api.plugin.connection_hook_spec import (
    ConnectionHookSpec,
)
from vdk.api.plugin.core_hook_spec import CoreHookSpecs
from vdk.api.plugin.core_hook_spec import JobRunHookSpecs
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal import cli_entry
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    ConnectionHookSpecFactory,
)
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    DefaultConnectionHookImpl,
)
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.managed_cursor import ManagedCursor
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.builtin_plugins.internal_hookspecs import InternalHookSpecs
from vdk.internal.builtin_plugins.run.data_job import DataJob
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.builtin_plugins.run.step import StepBuilder
from vdk.internal.builtin_plugins.run.step import StepFunction
from vdk.internal.cli_entry import CliEntry
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import StateStore
from vdk.internal.plugin.plugin import PluginRegistry
from vdk.plugin.test_utils.util_plugins import TestPropertiesPlugin
from vdk.plugin.test_utils.util_plugins import TestSecretsPlugin


def cli_assert(
    is_true: bool, result: Result, message: str = "result assert fails"
) -> None:
    """
    Test if some statement is true .
    If false error is raised with debug details about the CLI run taken from Result
    """
    assert is_true, (
        f"Message: {message} \n"
        f"Exception:\n {''.join(traceback.format_exception(*result.exc_info))} \n"
        f"Output:\n {result.output}"
    )


def cli_assert_equal(expected_exit_code: int, result: Result) -> None:
    """
    Test if exit code of a tested CLI run is as expected.
    If not error is raised with debug details about the CLI run.
    """
    cli_assert(
        result.exit_code == expected_exit_code,
        result,
        f"result exit code is not {expected_exit_code} but it is {result.exit_code}",
    )


def cli_assert_output_contains(expected_substring: str, result: Result) -> None:
    """
    Check if the output of a CLI run (logs or stdout) contains the passed expected substring.
    If not error is raised with debug details about the CLI run.
    """
    cli_assert(
        expected_substring in result.output,
        result,
        f"result output does not contain {expected_substring}",
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
        self._default_plugins = [TestPropertiesPlugin(), TestSecretsPlugin()]

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


def jobs_path_from_caller_directory(job_name: str) -> str:
    """
    Get data job path by looking at "jobs" directory. "jobs" directory is search in same one as caller's file directory.
    """
    caller_dir = get_caller_directory(2)
    return get_test_job_path(caller_dir, job_name)


def get_caller_directory(levels_up=1) -> pathlib.Path:
    """
    Get the directory containing the module that calls this function (levels_up = 1) or
    the module of the caller's caller (levels_up = 2), etc.
    """
    import inspect

    frame = inspect.stack()[levels_up]
    module = inspect.getmodule(frame[0])
    return pathlib.Path(os.path.dirname(os.path.abspath(module.__file__)))


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


def populate_mock_managed_cursor(
    mock_exception_to_recover=None,
    mock_operation=None,
    mock_parameters=None,
    decoration_operation_callback=None,
) -> (
    PEP249Cursor,
    ManagedCursor,
    DecorationCursor,
    RecoveryCursor,
    ConnectionHookSpec,
):
    import logging

    managed_operation = ManagedOperation(mock_operation, mock_parameters)
    mock_connection_hook_spec = MagicMock(spec=ConnectionHookSpec)
    connection_hook_spec_factory = MagicMock(spec=ConnectionHookSpecFactory)
    connection_hook_spec_factory.get_connection_hook_spec.return_value = (
        mock_connection_hook_spec
    )
    mock_native_cursor = MagicMock(spec=PEP249Cursor)

    managed_cursor = ManagedCursor(
        cursor=mock_native_cursor,
        log=logging.getLogger(),
        connection_hook_spec_factory=connection_hook_spec_factory,
    )

    decoration_cursor = DecorationCursor(mock_native_cursor, None, managed_operation)

    if decoration_operation_callback is None:
        decoration_operation_callback = (
            mock_connection_hook_spec.db_connection_decorate_operation
        )

    def stub_db_connection_execute_operation(execution_cursor: ExecutionCursor):
        return DefaultConnectionHookImpl().db_connection_execute_operation(
            execution_cursor
        )

    mock_connection_hook_spec.db_connection_execute_operation = (
        stub_db_connection_execute_operation
    )

    return (
        mock_native_cursor,
        managed_cursor,
        decoration_cursor,
        RecoveryCursor(
            native_cursor=mock_native_cursor,
            log=logging.getLogger(),
            exception=mock_exception_to_recover,
            managed_operation=managed_operation,
            decoration_operation_callback=decoration_operation_callback,
        ),
        mock_connection_hook_spec,
    )
