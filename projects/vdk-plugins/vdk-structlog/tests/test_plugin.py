# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.structlog import structlog_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


def test_structlog():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOGGING_METADATA": "timestamp,level,file_name,line_number,vdk_job_name,bound_test_key,extra_test_key"
        },
    ):
        runner = CliEntryBasedTestRunner(structlog_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("job-with-bound-logger")]
        )

        logs = result.stdout.split("\n")

        log_with_no_bound_context = [x for x in logs if "Log statement with no bound context" in x ][0]
        log_with_bound_context = [x for x in logs if "Log statement with bound context" in x][0]
        log_with_bound_and_extra_context = [x for x in logs if "Log statement with bound context and extra context" in x][0]

        # case 1
        # currently I'm getting the job name included on all steps, not sure if this is due to a bug in vdk-structlog

        # case 2
        assert "bound_test_value" in log_with_bound_context
        assert"bound_test_value" not in log_with_no_bound_context

        # case 3
        assert "extra_test_value" not in log_with_bound_context

        # case 4
        assert "extra_test_value" in log_with_bound_and_extra_context
        assert "bound_test_value" in  log_with_bound_and_extra_context

        # case 5 (continues in the next job run)
        # asserting one of the bound values does not appear in the logs since we've not configured it to appear
        assert "excluded_value" not in log_with_bound_context
        assert "excluded_value" not in log_with_bound_and_extra_context

        # asserting the log level and job name appear in the logs (so we can compare to when we exclude them below)
        assert "[INFO ]" in result.stdout
        assert "job-with-bound-logger" in result.stdout

    with mock.patch.dict(
            os.environ,
            {
                "VDK_LOGGING_METADATA": "timestamp,file_name,line_number,bound_test_key,extra_test_key"
            },
    ):
        runner = CliEntryBasedTestRunner(structlog_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("job-with-bound-logger")]
        )

        test_log = [x for x in result.stdout.split("\n") if "Log statement with bound context and extra context" in x][0]

        assert "[INFO ]" not in test_log
        assert "job-with-bound-logger" not in test_log
