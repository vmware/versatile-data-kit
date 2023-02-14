# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Optional
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.api.job_input import IJobInput
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.statestore import StoreKey
from vdk.plugin.test_utils.util_funcs import DataJobBuilder


def failing_runner_func(step: Step, job_input: IJobInput) -> bool:
    raise IndentationError("dummy")


def test_run_when_step_fails():
    job_builder = DataJobBuilder()
    job_builder.add_step_func(lambda s, i: True)
    job_builder.add_step_func(failing_runner_func)
    data_job = job_builder.build()

    result = data_job.run()
    assert result.is_failed()
    assert isinstance(result.get_exception_to_raise(), IndentationError)
    assert result.get_blamee() == ResolvableBy.USER_ERROR


def test_run_when_step_succeeds():
    job_builder = DataJobBuilder()
    job_builder.add_step_func(lambda s, i: True)
    result = job_builder.build().run()
    assert result.is_success()
    assert result.exception is None
    assert result.blamee is None


def test_run_job_with_default_hook():
    execution_result: ExecutionResult = None

    class MyPlugin:
        @hookimpl(hookwrapper=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            out: HookCallResult
            out = yield
            nonlocal execution_result
            execution_result = out.get_result()

    data = []

    def append_data_runner_func(step: Step, job_input: IJobInput) -> bool:
        data.append(1)
        return True

    job_builder = DataJobBuilder()
    job_builder.add_step_func(append_data_runner_func)
    job_builder.core_context.plugin_registry.load_plugin_with_hooks_impl(MyPlugin())
    job_builder.build().run()

    assert len(data) == 1
    assert data[0] == 1
    assert execution_result is not None and execution_result.is_success()


@patch("vdk.internal.core.statestore.StateStore.set")
@patch(
    "vdk.internal.core.statestore.StateStore.get", MagicMock(return_value=[])
)  # for creating child context
def test_run_not_from_template(mock_store_set):
    job_builder = DataJobBuilder()
    job_builder.build().run()
    assert not [
        c
        for c in mock_store_set.call_args_list
        if c[0][0] == StoreKey(key="vdk.template_name")
    ]


@patch("vdk.internal.core.statestore.StateStore.set")
@patch(
    "vdk.internal.core.statestore.StateStore.get", MagicMock(return_value=[])
)  # for creating child context
def test_run_from_template(mock_store_set):
    template_name = "template_name"
    job_builder = DataJobBuilder()
    job_builder.build().run(template_name=template_name)
    mock_store_set.assert_called_with(StoreKey(key="vdk.template_name"), template_name)
    assert (
        len(
            [
                c
                for c in mock_store_set.call_args_list
                if c[0][0] == StoreKey(key="vdk.template_name")
            ]
        )
        == 1
    )
