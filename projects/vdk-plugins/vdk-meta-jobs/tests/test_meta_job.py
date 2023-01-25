# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import time
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobExecution
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.meta_jobs import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Request
from werkzeug import Response


def _prepare(httpserver: PluginHTTPServer, jobs=None):
    """
    :param httpserver: the pytest http server
    :param jobs: list of jobs in format ('job-name', [list of http statuses to be returned], job result status)
    :return:
    """
    rest_api_url = httpserver.url_for("")
    team_name = "team-awesome"
    if jobs is None:
        jobs = [
            ("job1", [200], "succeeded", 0),
            ("job2", [200], "succeeded", 0),
            ("job3", [200], "succeeded", 0),
            ("job4", [200], "succeeded", 0),
        ]

    started_jobs = dict()

    for job_name, request_responses, job_status, *execution_duration in jobs:
        request_responses.reverse()
        execution_duration = execution_duration[0] if execution_duration else 0

        def handler(location, statuses, job_name):
            def _handler_fn(r: Request):
                status = statuses[0] if len(statuses) == 1 else statuses.pop()
                if status < 300:
                    started_jobs[job_name] = time.time()
                return Response(status=status, headers=dict(Location=location))

            return _handler_fn

        httpserver.expect_request(
            uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
            method="POST",
        ).respond_with_handler(
            handler(
                f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}",
                request_responses,
                job_name,
            )
        )

        def exec_handler(job_name, job_status, execution_duration):
            def _handler_fn(r: Request):
                actual_job_status = job_status
                if time.time() < started_jobs.get(job_name, 0) + execution_duration:
                    actual_job_status = "running"
                execution: DataJobExecution = DataJobExecution(
                    id=job_name,
                    job_name=job_name,
                    logs_url="http://url",
                    deployment=DataJobDeployment(),
                    start_time="2021-09-24T14:14:03.922Z",
                    status=actual_job_status,
                    message="foo",
                )
                response_data = json.dumps(execution.to_dict(), indent=4)
                return Response(
                    response_data,
                    status=200,
                    headers=None,
                    content_type="application/json",
                )

            return _handler_fn

        httpserver.expect_request(
            uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{job_name}",
            method="GET",
        ).respond_with_handler(exec_handler(job_name, job_status, execution_duration))

        def exec_list_handler(job_name):
            def _handler_fn(r: Request):
                execution: DataJobExecution = DataJobExecution(
                    id=f"{job_name}-latest",
                    job_name=job_name,
                    logs_url="http://url",
                    deployment=DataJobDeployment(),
                    start_time="2021-09-24T14:14:03.922Z",
                    status="succeeded",
                    message="foo",
                )
                response_data = json.dumps(execution.to_dict(), indent=4)
                return Response(
                    [response_data],
                    status=200,
                    headers=None,
                    content_type="application/json",
                )

            return _handler_fn

        httpserver.expect_request(
            uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions",
            method="GET",
        ).respond_with_handler(exec_list_handler(job_name))

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
        ("job1", [200], "succeeded"),
        ("job2", [200], "succeeded"),
        ("job3", [200], "platform_error"),
        ("job4", [200], "succeeded"),
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
        ("job1", [200], "succeeded"),
        ("job2", [200], "platform_error"),
        ("job3", [200], "succeeded"),
        ("job4", [200], "succeeded"),
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


def test_meta_job_conflict(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", [409, 200], "succeeded"),
        ("job2", [500, 200], "succeeded"),
        ("job3", [200], "succeeded"),
        ("job4", [200], "succeeded"),
    ]
    api_url = _prepare(httpserver, jobs)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_SERVICE_REST_API_URL": api_url,
            "VDK_META_JOBS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS": "0",
            "VDK_META_JOBS_DELAYED_JOBS_MIN_DELAY_SECONDS": "0",
        },
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("meta-job")]
        )
        cli_assert_equal(0, result)


def test_meta_job_cannot_start_job(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", [401, 200], "succeeded"),
        ("job2", [200], "succeeded"),
        ("job3", [200], "succeeded"),
        ("job4", [200], "succeeded"),
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
        # we should have 2 requests in the log, one to get a list
        # of all executions, and one for the failing data job
        # no other request should be tried as the meta job fails
        assert len(httpserver.log) == 2


def test_meta_job_long_running(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", [200], "succeeded", 3),  # execution duration is 3 seconds
        ("job2", [200], "succeeded"),
        ("job3", [200], "succeeded"),
        ("job4", [200], "succeeded"),
    ]
    api_url = _prepare(httpserver, jobs)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_SERVICE_REST_API_URL": api_url,
            # we set 5 seconds more than execution duration of 3 set above
            "VDK_META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS": "5",
            "VDK_META_JOBS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS": "0",
        },
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("meta-job")]
        )
        cli_assert_equal(0, result)
        job1_requests = [
            req
            for req, res in httpserver.log
            if req.method == "GET" and req.base_url.endswith("job1")
        ]
        # We have 1 call during start, 1 call at finish and 1 call that returns running and 1 that returns the final
        # status. For total of 4
        # NB: test (verification) that requires that deep implementation details knowledge is
        # not a good idea but we need to verify that we are not hammering the API Server somehow ...
        assert len(job1_requests) == 4

        # let's make sure something else is not generating more requests then expected
        # if implementation is changed the number below would likely change.
        # If the new count is not that big we can edit it here to pass the test,
        # if the new count is too big, we have an issue that need to be investigated.
        assert len(httpserver.log) == 21


def test_meta_job_circular_dependency(httpserver: PluginHTTPServer):
    jobs = [
        ("job1", [200], "succeeded"),
        ("job2", [200], "succeeded"),
        ("job3", [200], "succeeded"),
        ("job4", [200], "succeeded"),
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
            ["run", jobs_path_from_caller_directory("meta-job-circular-dep")]
        )
        cli_assert_equal(1, result)
        # no other request should be tried as the meta job fails
        assert isinstance(result.exception, UserCodeError)
        assert len(httpserver.log) == 0
