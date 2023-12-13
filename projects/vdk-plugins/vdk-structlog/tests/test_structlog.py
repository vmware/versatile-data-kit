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

# TODO: add vdk_step_name
# TODO: add vdk_step_type
STOCK_FIELDS = [
    "timestamp",
    "level",
    "file_name",
    "line_number",
    "function_name",
    "vdk_job_name",
]
STOCK_FIELD_REPRESENTATIONS = {
    "console": {
        "timestamp": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}",
        "level": r"\[INFO ]",
        "file_name": r"10_dummy\.py",
        "line_number": r"\s:[0-9]+",
        "function_name": "run",
        "vdk_job_name": JOB_NAME,
        "vdk_step_name": r"10_dummy\.py",
        "vdk_step_type": r"python",
    },
    "ltsv": {
        "timestamp": r"timestamp:\d+\.\d+",
        "level": r"level:INFO",
        "file_name": r"file_name:10_dummy\.py",
        "line_number": "line_number:[0-9]+",
        "function_name": "function_name:run",
        "vdk_job_name": f"vdk_job_name:{JOB_NAME}",
        "vdk_step_name": r"vdk_step_name:10_dummy\.py",
        "vdk_step_type": "vdk_step_type:python",
    },
    "json": {
        "timestamp": r'"timestamp": \d+\.\d+',
        "level": '"level": "INFO"',
        "file_name": '"filename": "10_dummy.py"',
        "line_number": '"lineno": [0-9]+',
        "function_name": '"funcName": "run"',
        "vdk_job_name": f'"vdk_job_name": "{JOB_NAME}"',
        "vdk_step_name": '"vdk_step_name": "10_dummy.py"',
        "vdk_step_type": '"vdk_step_type": "python"',
    },
}


@pytest.mark.parametrize("log_format", ["console", "ltsv", "json"])
def test_structlog(log_format):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": f"timestamp,level,file_name,line_number,vdk_job_name,{BOUND_TEST_KEY},{EXTRA_TEST_KEY}",
            "VDK_LOGGING_FORMAT": log_format,
            "LOG_LEVEL_MODULE": "test_structlog=WARNING",
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

        # due to the log_level_module config specified in the config.ini of the test job
        # the 'This log statement should not appear' log should not appear in the output logs
        assert (
            _get_log_containing_s(logs, "This log statement should not appear") is None
        )

        _assert_cases(
            log_with_no_bound_context,
            log_with_bound_context,
            log_with_bound_and_extra_context,
        )


@pytest.mark.parametrize("log_format", ["console", "ltsv", "json"])
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

            # check that the removed_field is not shown in the log
            assert re.search(stock_field_reps[removed_field], test_log) is None

            # check the rest are shown
            for shown_field in shown_fields:
                assert re.search(stock_field_reps[shown_field], test_log) is not None


@pytest.mark.parametrize("log_format", ["console"])
def test_custom_format_applied(log_format):
    custom_format_string = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_FORMAT": log_format,
            "VDK_CUSTOM_CONSOLE_LOG_PATTERN": custom_format_string,
        },
    ):
        logs = _run_job_and_get_logs()

        for log in logs:
            if "Log statement with no bound context" in log:
                assert _matches_custom_format(log)
                break
        else:
            pytest.fail("Log statement with no bound context not found in logs")


@pytest.mark.parametrize("log_format", ["json", "ltsv"])
def test_custom_format_not_applied_for_non_console_formats(log_format):
    custom_format_string = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": "timestamp,level,file_name,vdk_job_name",
            "VDK_LOGGING_FORMAT": log_format,
            "VDK_CUSTOM_CONSOLE_LOG_PATTERN": custom_format_string,
        },
    ):
        logs = _run_job_and_get_logs()

        for log in logs:
            if "Log statement with no bound context" in log:
                assert not _matches_custom_format(
                    log
                ), f"Custom format was incorrectly applied for {log_format} format. Log: {log}"
                break
        else:
            pytest.fail("Log statement with no bound context not found in logs")


@pytest.mark.parametrize("log_format", ["console", "json", "ltsv"])
def test_step_name_step_type(log_format):
    stock_field_reps = STOCK_FIELD_REPRESENTATIONS[log_format]
    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": "vdk_step_type,vdk_step_name",
            "VDK_LOGGING_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is not None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is not None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": "vdk_step_name",
            "VDK_LOGGING_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is not None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": "vdk_step_type",
            "VDK_LOGGING_FORMAT": log_format,
        },
    ):
        logs = _run_job_and_get_logs()
        test_log = _get_log_containing_s(logs, "Log statement with no bound context")
        assert re.search(stock_field_reps["vdk_step_name"], test_log) is None
        assert re.search(stock_field_reps["vdk_step_type"], test_log) is not None


def _matches_custom_format(log):
    pattern = re.compile(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \S{1,12} \S{1,8} .+"
    )
    return bool(pattern.search(log))


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
    necessary_log = [x for x in logs if s in x]
    if len(necessary_log) == 0:
        return None
    else:
        return necessary_log[0]


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
