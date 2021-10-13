# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from typing import Optional
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


@mock.patch.dict(
    os.environ,
    {
        "VDK_OP_ID": "my-op-id",
        "VDK_EXECUTION_ID": "my-execution-id",
        "VDK_ATTEMPT_ID": "my-attempt-id",
    },
)
def test_run_check_attempt_execution_op_id_are_set_correctly():
    actual_ids = []

    class PrintIdPlugin:
        @hookimpl(tryfirst=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            actual_ids.append(
                context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
            )
            actual_ids.append(
                context.core_context.state.get(CommonStoreKeys.EXECUTION_ID)
            )
            actual_ids.append(context.core_context.state.get(CommonStoreKeys.OP_ID))
            return None  # continue with next hook impl.

    runner = CliEntryBasedTestRunner(PrintIdPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])

    cli_assert_equal(0, result)
    assert actual_ids == ["my-attempt-id", "my-execution-id", "my-op-id"]
