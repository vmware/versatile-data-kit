# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from vdk.plugin.structlog import structlog_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

JOB_NAME = "job-with-bound-logger"
BOUND_TEST_KEY = "bound_test_key"
BOUND_TEST_VALUE = "bound_test_value"
EXTRA_TEST_KEY = "extra_test_key"
EXTRA_TEST_VALUE = "extra_test_value"
EXCLUDED_VALUE = "excluded_value"


STOCK_FIELDS = ["level", "file_name", "line_number", "vdk_job_name"]
STOCK_FIELD_REPRESENTATIONS = {
    "level": "INFO",
    "file_name": "10_dummy.py",
    "line_number": ":23",
    "vdk_job_name": JOB_NAME,
}


def test_structlog_console():
    for log_format in ["console", "json"]:
        with mock.patch.dict(
            os.environ,
            {
                "VDK_LOGGING_METADATA": f"timestamp,level,file_name,line_number,vdk_job_name,{BOUND_TEST_KEY},{EXTRA_TEST_KEY}",
                "VDK_LOGGING_FORMAT": log_format,
            },
        ):
            runner = CliEntryBasedTestRunner(structlog_plugin)

            result: Result = runner.invoke(
                ["run", jobs_path_from_caller_directory("job-with-bound-logger")]
            )

            logs = result.output.split("\n")

            log_with_no_bound_context = [
                x for x in logs if "Log statement with no bound context" in x
            ][0]
            log_with_bound_context = [
                x for x in logs if "Log statement with bound context" in x
            ][0]
            log_with_bound_and_extra_context = [
                x
                for x in logs
                if "Log statement with bound context and extra context" in x
            ][0]

            _assert_cases(
                log_with_no_bound_context,
                log_with_bound_context,
                log_with_bound_and_extra_context,
            )

        for removed_field in STOCK_FIELDS:
            shown_fields = [field for field in STOCK_FIELDS if field != removed_field]

            with mock.patch.dict(
                os.environ,
                {
                    "VDK_LOGGING_METADATA": ",".join(shown_fields)
                    + "bound_test_key,extra_test_key"
                },
            ):
                runner = CliEntryBasedTestRunner(structlog_plugin)

                result: Result = runner.invoke(
                    ["run", jobs_path_from_caller_directory("job-with-bound-logger")]
                )

                test_log = [
                    x
                    for x in result.output.split("\n")
                    if "Log statement with bound context and extra context" in x
                ][0]

                # check that the removed_field in not shown in the log
                assert STOCK_FIELD_REPRESENTATIONS[removed_field] not in test_log


def _assert_cases(
    log_with_no_bound_context, log_with_bound_context, log_with_bound_and_extra_context
):
    # check for job name in logs
    assert (
        (JOB_NAME in log_with_no_bound_context)
        and (JOB_NAME in log_with_bound_context)
        and (JOB_NAME in log_with_bound_and_extra_context)
    )

    # check bound logger can bind context but that bound context does not appear in the rest of logging
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
    assert (EXCLUDED_VALUE not in log_with_bound_context) and (
        EXCLUDED_VALUE not in log_with_bound_and_extra_context
    )

    # check the log level and job name appear in the logs (so we can compare to when we exclude them below)
    assert ("INFO" in log_with_no_bound_context) and (
        JOB_NAME in log_with_no_bound_context
    )
