# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import asdict

import pytest
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.builtin_plugins.run.summary_output import JobSummary
from vdk.internal.builtin_plugins.run.summary_output import JobSummaryParser
from vdk.internal.builtin_plugins.run.summary_output import StepSummary
from vdk.internal.core.errors import ErrorType

# Test data
step1 = StepSummary(
    name="step1", status=ExecutionStatus.SUCCESS, blamee=None, details="details1"
)
step2 = StepSummary(
    name="step2",
    status=ExecutionStatus.ERROR,
    blamee=ErrorType.USER_ERROR,
    details="details2",
)
step3 = StepSummary(
    name="step3",
    status=ExecutionStatus.ERROR,
    blamee=ErrorType.PLATFORM_ERROR,
    details="details3",
)
job_summary = JobSummary(
    steps=[step1, step2, step3],
    status=ExecutionStatus.SUCCESS,
    blamee=None,
    details="Job details",
)


def test_to_json():
    json_str = JobSummaryParser.to_json(job_summary)
    assert json.loads(json_str) == asdict(job_summary)


def test_from_json():
    json_str = JobSummaryParser.to_json(job_summary)
    parsed_job_summary = JobSummaryParser.from_json(json_str)
    assert parsed_job_summary == job_summary


def test_from_empty_json():
    parsed_job_summary = JobSummaryParser.from_json("{}")
    assert parsed_job_summary.steps == []
    assert parsed_job_summary.status is None
    assert parsed_job_summary.blamee is None
    assert parsed_job_summary.details is None


def test_from_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        JobSummaryParser.from_json("not a json string")
