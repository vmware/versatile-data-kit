# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum
from enum import IntEnum


class RunStatus(IntEnum):
    """
    The status of a data job run
    """

    SUCCESS = 0
    PLATFORM_ERROR = 1
    USER_ERROR = 2
    RUNNING = 3


class ExecutionStatus(str, Enum):
    """
    Just a few constants
    """

    SUCCESS = "success"
    NOT_RUNNABLE = "not_runnable"
    ERROR = "error"
