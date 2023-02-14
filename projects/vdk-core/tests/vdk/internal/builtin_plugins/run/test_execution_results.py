# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime

from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.core import errors
from vdk.internal.core.errors import ResolvableBy


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
        [],
        None,
        None,
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
  "exception": null,
  "blamee": null
}"""
    )


def test_get_exception_to_raise():
    step_error = ArithmeticError("foo")
    result = _prepare_execution_result(None, step_error)
    assert result.get_exception_to_raise() == step_error


def test_get_exception_to_raise_main_error():
    step_error = ArithmeticError("foo")
    error = IndexError("foo")
    result = _prepare_execution_result(error, step_error)
    assert result.get_exception_to_raise() == error


def _prepare_execution_result(error, step_error, blamee=None):
    step_result = StepResult(
        "step",
        "type",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 00:30:00"),
        ExecutionStatus.ERROR,
        "foo",
        step_error,
        errors.ResolvableBy.USER_ERROR,
    )
    result = ExecutionResult(
        "job-name",
        "exec-id",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.SUCCESS,
        [step_result],
        error,
        blamee,
    )
    return result


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
        ResolvableBy.USER_ERROR,
    )
    result = ExecutionResult(
        "job-name",
        "exec-id",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.ERROR,
        [step_result],
        exception,
        ResolvableBy.USER_ERROR,
    )

    result_as_string = result.__repr__()
    assert json.loads(result_as_string) is not None


def test_serialization_circular_reference():
    exception = ArithmeticError("foo")
    exception.__cause__ = exception
    step_result = StepResult(
        "step",
        "type",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.ERROR,
        "details",
        exception,
        ResolvableBy.USER_ERROR,
    )
    result = ExecutionResult(
        "job-name",
        "exec-id",
        datetime.fromisoformat("2012-10-12 00:00:00"),
        datetime.fromisoformat("2012-10-12 01:00:00"),
        ExecutionStatus.ERROR,
        [step_result],
        exception,
        ResolvableBy.USER_ERROR,
    )

    result_as_string = result.__repr__()
    assert result_as_string is not None
