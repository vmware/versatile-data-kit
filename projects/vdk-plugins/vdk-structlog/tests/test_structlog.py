# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import re
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.structlog import structlog_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

JOB_NAME = "job-with-bound-logger"
BOUND_TEST_KEY = "bound_test_key"
BOUND_TEST_VALUE = "bound_test_value"
EXTRA_TEST_KEY = "extra_test_key"
EXTRA_TEST_VALUE = "extra_test_value"
EXCLUDED_BOUND_TEST_KEY = "excluded_bound_test_key"
EXCLUDED_BOUND_TEST_VALUE = "excluded_bound_test_value"

STOCK_FIELDS = [
    "level",
    "file_name",
    "line_number",
    "vdk_job_name",
]  # TODO: add timestamp once bug is resolved
STOCK_FIELD_REPRESENTATIONS = {
    "console": {
        "level": r"\[INFO ]",
        "file_name": r"10_dummy\.py",
        "line_number": ":[0-9]+",
        "vdk_job_name": JOB_NAME,
    },
    "json": {
        "level": '"level": "INFO"',
        "file_name": '"filename:":"10_dummy.py"',
        "line_number": '"lineno": [0-9]+',
        "vdk_job_name": f'"vdk_job_name": "{JOB_NAME}"',
    },
}


@pytest.mark.parametrize(
    "log_format", ["console"]
)  # TODO: replace with ["console","json"] once the issue where fields can't be excluded in JSON is fixed
def test_structlog(log_format):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": f"timestamp,level,file_name,line_number,vdk_job_name,{BOUND_TEST_KEY},{EXTRA_TEST_KEY}",
            "VDK_LOGGING_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()

        log_with_no_bound_context = _get_log_containing_s(
            logs, "Log statement with no bound context"
        )
        log_with_bound_context = _get_log_containing_s(
            logs, "Log statement with bound context"
        )
        log_with_bound_and_extra_context = _get_log_containing_s(
            logs, "Log statement with bound context and extra context"
        )

        _assert_cases(
            log_with_no_bound_context,
            log_with_bound_context,
            log_with_bound_and_extra_context,
        )


@pytest.mark.parametrize(
    "log_format", ["console"]
)  # TODO: replace with ["console", "json"] once the issue where fields can't be excluded in JSON is fixed
def test_stock_fields_removal(log_format):
    stock_field_reps = STOCK_FIELD_REPRESENTATIONS[log_format]

    for removed_field in STOCK_FIELDS:
        shown_fields = [field for field in STOCK_FIELDS if field != removed_field]
        vdk_logging_metadata = ",".join(shown_fields) + ",bound_test_key,extra_test_key"

        with mock.patch.dict(
            os.environ,
            {
                "VDK_LOGGING_METADATA": vdk_logging_metadata,
                "VDK_LOGGING_FORMAT": log_format,
            },
        ):
            logs = _run_job_and_get_logs()

            test_log = _get_log_containing_s(
                logs, "Log statement with bound context and extra context"
            )

            # check that the removed_field in not shown in the log
            assert re.search(stock_field_reps[removed_field], test_log) is None

            # check the rest are shown
            for shown_field in shown_fields:
                assert re.search(stock_field_reps[shown_field], test_log) is not None


def _run_job_and_get_logs():
    """
    Runs the necessary job and returns the output logs.

    :return: Job logs
    """
    runner = CliEntryBasedTestRunner(structlog_plugin)

    result: Result = runner.invoke(
        [
            "run",
            "--arguments",
            _get_job_arguments(),
            jobs_path_from_caller_directory("job-with-bound-logger"),
        ]
    )

    return result.output.split("\n")


def _get_log_containing_s(logs, s):
    """
    Given a list of logs and a string, returns the first log which contains the string
    :param logs:
    :param s:
    :return:
    """
    try:
        necessary_log = [x for x in logs if s in x][0]
    except IndexError as e:
        raise Exception("Log cannot be found inside provided job logs") from e

    return necessary_log


def _assert_cases(
    log_with_no_bound_context, log_with_bound_context, log_with_bound_and_extra_context
):
    # check for job name in logs
    assert (
        (JOB_NAME in log_with_no_bound_context)
        and (JOB_NAME in log_with_bound_context)
        and (JOB_NAME in log_with_bound_and_extra_context)
    )

    # check that bound logger can bind context but that bound context does not appear in the rest of logging
    assert (BOUND_TEST_VALUE in log_with_bound_context) and (
        BOUND_TEST_VALUE not in log_with_no_bound_context
    )

    # check extra bound context does not appear if not set in the logging_metadata config variable
    assert EXTRA_TEST_VALUE not in log_with_bound_context

    # check for both the bound and the extra context in bound log statements which include extra context
    assert (EXTRA_TEST_VALUE in log_with_bound_and_extra_context) and (
        BOUND_TEST_VALUE in log_with_bound_and_extra_context
    )

    # check that one of the bound values does not appear in the logs since we've not configured it to appear
    assert (EXCLUDED_BOUND_TEST_VALUE not in log_with_bound_context) and (
        EXCLUDED_BOUND_TEST_VALUE not in log_with_bound_and_extra_context
    )

    # check the log level and job name appear in the logs (so we can compare to when we exclude them below)
    assert ("INFO" in log_with_no_bound_context) and (
        JOB_NAME in log_with_no_bound_context
    )


def _get_job_arguments():
    bound_fields = f'{{"{BOUND_TEST_KEY}": "{BOUND_TEST_VALUE}", "{EXCLUDED_BOUND_TEST_KEY}": "{EXCLUDED_BOUND_TEST_VALUE}"}}'
    extra_fields = f'{{"{EXTRA_TEST_KEY}": "{EXTRA_TEST_VALUE}"}}'

    return f'{{"bound_fields": {bound_fields}, "extra_fields": {extra_fields}}}'
