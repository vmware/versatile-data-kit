# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime

from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult
from taurus.vdk.builtin_plugins.run.execution_results import StepResult
from taurus.vdk.builtin_plugins.run.run_status import ExecutionStatus


class NonJsonSerializable:
    # slots mean we do not have __dict__
    __slots__ = "item"

    def __init__(self, item):
        self.item = item


class MyException(Exception):
    def __init__(self, arg: NonJsonSerializable):
        self.arg = arg


def dummy_step_func(step, job_input) -> bool:
    return True


def test_serialization():
    result = ExecutionResult(
        "job-name",
        "exec-id",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.SUCCESS,
        None,
        [],
    )

    assert (
        result.__repr__()
        == """{
  "data_job_name": "job-name",
  "execution_id": "exec-id",
  "start_time": "2012-10-12T00:00:00",
  "end_time": "2012-10-12T01:00:00",
  "status": "success",
  "steps_list": [],
  "exception": null
}"""
    )


def test_serialization_non_serializable():
    exception = MyException(NonJsonSerializable(1))
    step_result = StepResult(
        "step",
        "type",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.ERROR,
        "details",
        exception,
    )
    result = ExecutionResult(
        "job-name",
        "exec-id",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.ERROR,
        exception,
        [step_result],
    )

    result_as_string = result.__repr__()
    assert json.loads(result_as_string) is not None
