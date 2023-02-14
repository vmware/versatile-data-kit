# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.core.statestore import StoreKey


class ExecutionStateStoreKeys:
    """
    Keys used to keep data about data job execution (or run) state
    """

    JOB_NAME: StoreKey[str] = StoreKey("vdk.job_name")
    JOB_GIT_HASH: StoreKey[str] = StoreKey("vdk.job_git_hash")
    STEPS_SUCCEEDED: StoreKey[List[str]] = StoreKey("vdk.steps_succeeded")
    STEPS_STARTED: StoreKey[List[str]] = StoreKey("vdk.steps_started")
    STEPS_FAILED: StoreKey[List[str]] = StoreKey("vdk.steps_failed")
    EXECUTION_RESULT: StoreKey[Optional[ExecutionResult]] = StoreKey(
        "vdk.execution_result"
    )
    TEMPLATE_NAME: StoreKey[str] = StoreKey("vdk.template_name")
