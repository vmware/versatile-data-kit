# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobExecution
from vdk.plugin.meta_jobs import plugin_entry
from vdk.plugin.meta_jobs.remote_data_job import JobStatus
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Response


def _prepare(httpserver: PluginHTTPServer, jobs=None):
    rest_api_url = httpserver.url_for("")
    team_name = "team-awesome"
    if jobs is None:
        jobs = [
            ("job1", 200, "succeeded"),
            ("job2", 200, "succeeded"),
            ("job3", 200, "succeeded"),
            ("job4", 200, "succeeded"),
        ]

    for job_name, request_response, job_status in jobs:
        httpserver.expect_request(
            uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
            method="POST",
        ).respond_with_response(
            Response(
                status=request_response,
                headers=dict(
                    Location=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}"
                ),
            )
        )

        execution: DataJobExecution = DataJobExecution(
            id=job_name,
            job_name=job_name,
            logs_url="http://url",
            deployment=DataJobDeployment(),
            start_time="2021-09-24T14:14:03.922Z",
            status=job_status,
            message="foo",
        )
        httpserver.expect_request(
            uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}",
            method="GET",
        ).respond_with_json(execution.to_dict())

    return rest_api_url


def test_meta_job(httpserver: PluginHTTPServer):
    api_url = _prepare(httpserver)

    with mock.patch.dict(
        os.environ,
        {"VDK_CONTROL_SERVICE_REST_API_URL": api_url},
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("meta-job")]
        )
        cli_assert_equal(0, result)


def test_meta_job_error(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", 200, "succeeded"),
        ("job2", 200, "succeeded"),
        ("job3", 200, "platform_error"),
        ("job4", 200, "succeeded"),
    ]
    api_url = _prepare(httpserver, jobs)

    with mock.patch.dict(
        os.environ,
        {"VDK_CONTROL_SERVICE_REST_API_URL": api_url},
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("meta-job")]
        )
        cli_assert_equal(1, result)


def test_meta_job_fail_false(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", 200, "succeeded"),
        ("job2", 200, "platform_error"),
        ("job3", 200, "succeeded"),
        ("job4", 200, "succeeded"),
    ]
    api_url = _prepare(httpserver, jobs)

    with mock.patch.dict(
        os.environ,
        {"VDK_CONTROL_SERVICE_REST_API_URL": api_url},
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("meta-job")]
        )
        cli_assert_equal(0, result)
