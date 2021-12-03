# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.core import errors
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import PlatformServiceError


@dataclass(frozen=True)
class StepResult:
    """
    The result of a step execution
    """

    # the name of the concrete step (e.g name of the file)
    name: str
    # TYPE_SQL, TYPE_PYTHON  or user-defined type
    type: str
    # when did the step started
    start_time: datetime
    # when did it finish
    end_time: datetime
    # status ?
    status: ExecutionStatus
    # string with details.
    details: Optional[str]
    # Exception if thrown
    exception: Optional[BaseException] = None
    # who is responsible for resolving the error
    blamee: Optional[errors.ResolvableBy] = None


class ExecutionResult:
    """
    Keep the execution result of a data job run.
    """

    def __init__(
        self,
        data_job_name: str,
        execution_id: str,
        start_time: datetime,
        end_time: datetime,
        status: ExecutionStatus,
        exception: Optional[BaseException],
        steps_list: List[StepResult],
    ):
        self.data_job_name = data_job_name
        self.execution_id = execution_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.steps_list = steps_list
        self.exception = exception

    def is_failed(self):
        return self.status == ExecutionStatus.ERROR

    def is_success(self):
        return self.status == ExecutionStatus.SUCCESS

    def get_exception(self):
        """
        Deprecated in favour of #get_exception_to_raise()
        """
        return self.get_exception_to_raise()

    def get_exception_to_raise(self):
        """
        Returns main exception to be used as a failure reason for the data job.
        """
        if self.exception:
            return self.exception
        step_exceptions = map(lambda x: x.exception, self.steps_list)
        step_exception = next(filter(lambda e: e is not None, step_exceptions), None)
        if step_exception:
            return step_exception
        else:
            return PlatformServiceError(
                ErrorMessage(
                    f"Data Job {self.data_job_name} failed",
                    "Data Job has failed",
                    "Failure is with unspecified reason. Seems like a bug in VDK.",
                    "Job will not complete",
                    "Retry the job. "
                    "Consider opening a ticket https://github.com/vmware/versatile-data-kit/issues",
                )
            )

    def __repr__(self):
        data = self.__dict__.copy()
        # make dates more human-readble
        data["start_time"] = self.start_time.isoformat()
        data["end_time"] = self.end_time.isoformat()
        if self.exception:
            data["exception_name"] = str(self.exception.__class__.__name__)

        step_lists_of_dicts = list()
        for step in self.steps_list:
            d = step.__dict__.copy()
            d["start_time"] = d["start_time"].isoformat()
            d["end_time"] = d["end_time"].isoformat()
            if step.exception:
                d["exception_name"] = str(step.exception.__class__.__name__)
                if step.exception.__cause__:
                    setattr(
                        d["exception"],
                        "cause_exception_name",
                        step.exception.__cause__.__class__.__name__,
                    )
                    setattr(
                        d["exception"],
                        "cause_exception",
                        step.exception.__cause__.__dict__,
                    )
            step_lists_of_dicts.append(d)

        data["steps_list"] = step_lists_of_dicts

        def default_serialization(o: Any) -> Any:
            return o.__dict__ if "__dict__" in dir(o) else str(o)

        return json.dumps(data, default=default_serialization, indent=2)
