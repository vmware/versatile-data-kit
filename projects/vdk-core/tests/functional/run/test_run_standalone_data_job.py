# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import collections
from pathlib import Path
from typing import List

import pytest
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.standalone_data_job import (
    StandaloneDataJobFactory,
)
from vdk.internal.builtin_plugins.run.step import Step

ExecutedStandaloneDataJobDetails = collections.namedtuple(
    "ExecutedStandalongDataJob", "hook_tracker job_input_name"
)


@pytest.fixture
def executed_standalone_data_job():
    hook_tracker = util.HookCallTracker()
    job_input_name = "unknown"

    with StandaloneDataJobFactory.create(
        data_job_directory=Path(__file__), extra_plugins=[hook_tracker]
    ) as job_input:
        job_input_name = job_input.get_name()

    return ExecutedStandaloneDataJobDetails(
        hook_tracker=hook_tracker,
        job_input_name=job_input_name,
    )


def test_standalone_data_job_named_after_data_job_directory(
    executed_standalone_data_job,
):
    assert executed_standalone_data_job.job_input_name == Path(__file__).name


def test_standalone_data_job_executes_hooks_in_expected_order(
    executed_standalone_data_job,
):
    assert (
        ", ".join(executed_standalone_data_job.hook_tracker.calls)
        == "vdk_start, vdk_configure, vdk_initialize, initialize_job, run_job, run_step, finalize_job, vdk_exit"
    )


def test_standalone_data_job_does_not_call_command_line_hook(
    executed_standalone_data_job,
):
    assert "vdk_command_line" not in executed_standalone_data_job.hook_tracker.calls


def test_standalone_data_job_does_calls_exception_hook_after_exception_thrown():
    hook_tracker = util.HookCallTracker()

    with pytest.raises(ValueError) as exc_info:
        with StandaloneDataJobFactory.create(
            data_job_directory=Path(__file__), extra_plugins=[hook_tracker]
        ):
            raise ValueError("Test Error")

    assert "vdk_exception" in hook_tracker.calls
    assert str(exc_info.value) == "Test Error"


def test_standalone_data_job_not_from_template():
    data_job = StandaloneDataJobFactory.create(data_job_directory=Path(__file__))
    assert not data_job._template_name
    assert not data_job._core_context.state.get(ExecutionStateStoreKeys.TEMPLATE_NAME)


def test_standalone_data_job_from_template():
    template_name = "template_name"
    data_job = StandaloneDataJobFactory.create(
        data_job_directory=Path(__file__), template_name=template_name
    )
    assert data_job._template_name == template_name
    assert (
        data_job._core_context.state.get(ExecutionStateStoreKeys.TEMPLATE_NAME)
        == template_name
    )


def test_standalone_data_job_handles_arguments():
    job_args = {"arg1": "value1", "arg2": "value2"}

    with StandaloneDataJobFactory.create(
        data_job_directory=Path(__file__).parent, job_args=job_args
    ) as job_input:
        assert job_input.get_arguments() == job_args


def test_standalone_data_job_passes_command_line_arguments():
    class CommandLineCatcher:
        def __init__(self):
            self.command_line_args = []

        @hookimpl
        def vdk_start(
            self, plugin_registry: "IPluginRegistry", command_line_args: List
        ) -> None:
            self.command_line_args = command_line_args

    job_dir = Path(__file__).parent
    cmd_line_catcher = CommandLineCatcher()

    with StandaloneDataJobFactory.create(
        data_job_directory=job_dir, extra_plugins=[cmd_line_catcher]
    ) as job_input:
        assert cmd_line_catcher.command_line_args == ["run", str(job_dir)]

    with StandaloneDataJobFactory.create(
        data_job_directory=job_dir,
        extra_plugins=[cmd_line_catcher],
        job_args={"a": "b"},
    ) as job_input:
        assert cmd_line_catcher.command_line_args == [
            "run",
            str(job_dir),
            "--arguments",
            '{"a": "b"}',
        ]


def test_standalone_data_job_ignore_steps_added_by_other_plugins(
    executed_standalone_data_job,
):
    class AddNewStep:
        def __init__(self):
            self.step_executed = []

        @hookimpl
        def initialize_job(self, context: JobContext):
            def func(_step, _job_input):
                self.step_executed.append("")
                return True

            step = Step(
                name="NoOpStep",
                type="noop",
                runner_func=func,
                file_path=Path(__file__),
                job_dir=context.job_directory,
            )
            context.step_builder.add_step(step)

    new_step_plugin = AddNewStep()
    with StandaloneDataJobFactory.create(
        data_job_directory=Path(__file__), extra_plugins=[new_step_plugin]
    ) as job_input:
        pass

    assert len(new_step_plugin.step_executed) == 0
