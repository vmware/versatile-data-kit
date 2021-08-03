# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pluggy
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config import vdk_config
from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult
from taurus.vdk.builtin_plugins.run.execution_results import StepResult
from taurus.vdk.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.builtin_plugins.run.run_status import ExecutionStatus
from taurus.vdk.builtin_plugins.run.step import Step


class ExecutionTrackingPlugin:
    """
    We are going to track data job executions in this plugin and update the statestore of the execution.
    """

    @hookimpl
    def initialize_job(self, context: JobContext):

        state = context.core_context.state
        configuration = context.core_context.configuration

        state.set(ExecutionStateStoreKeys.JOB_NAME, context.name)
        state.set(
            ExecutionStateStoreKeys.JOB_GIT_HASH,
            configuration.get_value(vdk_config.JOB_GITHASH),
        )
        state.set(ExecutionStateStoreKeys.STEPS_STARTED, [])
        state.set(ExecutionStateStoreKeys.STEPS_SUCCEEDED, [])
        state.set(ExecutionStateStoreKeys.STEPS_FAILED, [])
        state.set(ExecutionStateStoreKeys.EXECUTION_RESULT, None)

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> None:
        """The script that runs the actual run of the data job.
        It executes the provided steps starting from context.step_tree_root in sequential order (using BFS)
        using
        """
        out: pluggy.callers._Result
        out = yield

        result: ExecutionResult = out.get_result()
        state = context.core_context.state
        state.set(ExecutionStateStoreKeys.EXECUTION_RESULT, result)

    @hookimpl(hookwrapper=True)
    def run_step(self, context: JobContext, step: Step) -> None:
        state = context.core_context.state

        state.get(ExecutionStateStoreKeys.STEPS_STARTED).append(step.name)
        out: pluggy.callers._Result
        out = yield
        if out.excinfo:
            state.get(ExecutionStateStoreKeys.STEPS_FAILED).append(step.name)

        result: StepResult = out.get_result()  # will throw if there was an exception
        if result.status == ExecutionStatus.SUCCESS:
            state.get(ExecutionStateStoreKeys.STEPS_SUCCEEDED).append(step.name)
        elif result.status == ExecutionStatus.ERROR:
            state.get(ExecutionStateStoreKeys.STEPS_FAILED).append(step.name)
