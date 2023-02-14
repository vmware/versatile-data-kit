# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
from json import JSONDecodeError
from typing import Any
from typing import List

import werkzeug
from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.httpserver import QueryMatcher
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.list import list_command

test_utils.disable_vdk_authentication()


def get_data_job_query_response(jobs: List[Any]):
    return dict(data=dict(content=jobs, errors=[]))


def get_example_data_job_query_response():
    jobs = [
        {
            "jobName": "test-job",
            "config": {
                "team": "test-team",
                "description": "test-job description",
                "schedule": {"schedule_cron": "11 23 5 8 1"},
            },
            "deployments": [{"enabled": True}],
        },
        {
            "jobName": "test-job-2",
            "config": {
                "team": "test-team",
                "description": "test-job-2 description",
                "schedule": {"schedule_cron": "11 23 5 8 1"},
            },
            "deployments": [{"enabled": False}],
        },
        {
            "jobName": "test-job-3",
            "config": {
                "team": "test-team",
                "description": "test-job-2 description",
            },
            "deployments": [],
        },
    ]
    return get_data_job_query_response(jobs)


def test_list_default_all(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    response = get_example_data_job_query_response()

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(list_command, ["-t", "test-team", "-u", rest_api_url])
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "test-job" in result.output and "test-job-2" in result.output
    ), f"expected data not found in output: {result.output} "


def test_list_all(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    response = get_data_job_query_response(
        [
            {
                "jobName": f"test-job-1",
                "config": {
                    "team": "test-team",
                    "description": f"test-job-1 description",
                },
                "deployments": [],
            }
        ]
    )

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs",
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(list_command, ["-t", "test-team", "-a", "-u", rest_api_url])
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "test-job" in result.output
    ), f"expected data not found in output: {result.output} "

    result = runner.invoke(
        list_command, ["-t", "test-team", "--all", "-u", rest_api_url]
    )
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "test-job" in result.output
    ), f"expected data not found in output: {result.output} "

    httpserver.expect_request(
        uri="/data-jobs/for-team/no-team-specified/jobs",
    ).respond_with_json(response)

    result = runner.invoke(list_command, ["-u", rest_api_url])
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "test-job" in result.output
    ), f"expected data not found in output: {result.output} "


def test_list_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(list_command, ["-t", "test-team"])

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_list_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(list_command, ["-t", "test-team", "-u", ""])

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_list_with_json_output(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    response = get_example_data_job_query_response()

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(
        list_command, ["-t", "test-team", "-u", rest_api_url, "-o", "json"]
    )
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"

    try:
        json_result = json.loads(result.output)
    except JSONDecodeError as error:
        assert False, f"failed to parse the response as a JSON object, error: {error}"
    assert isinstance(json_result, list)
    assert len(list(json_result)) == 3
    assert list(json_result)[0]["job_name"] == "test-job"


def test_list_with_invalid_output(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    runner = CliRunner()
    result = runner.invoke(
        list_command, ["-t", "test-team", "-u", rest_api_url, "-o", "invalid"]
    )
    assert (
        result.exit_code == 2
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "Error: Invalid value for '--output'" in result.output
    ), f"expected data not found in output: {result.output}"


def test_list_with_multiple_pages(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    def job(i):
        return {
            "jobName": f"test-job-{i}",
            "config": {
                "team": "test-team",
                "description": f"test-job-{i} description",
            },
            "deployments": [],
        }

    page1 = get_data_job_query_response(list(map(lambda j: job(j), range(1, 101))))
    page2 = get_data_job_query_response(list(map(lambda j: job(j), range(101, 121))))

    class ContainsQueryMatcher(QueryMatcher):
        def __init__(self, substring: str):
            self.__substring = substring

        def get_comparing_values(self, request_query_string: bytes) -> tuple:
            query_string = werkzeug.urls.url_decode(request_query_string)

            return self.__substring in str(query_string), True

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs",
        query_string=ContainsQueryMatcher("pageNumber: 1"),
    ).respond_with_json(page1)
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs",
        query_string=ContainsQueryMatcher("pageNumber: 2"),
    ).respond_with_json(page2)
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs",
        query_string=ContainsQueryMatcher("pageNumber: 3"),
    ).respond_with_json([])

    runner = CliRunner()
    result = runner.invoke(list_command, ["-t", "test-team", "-a", "-u", rest_api_url])
    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}, exc: {result.exc_info}"
    assert (
        "test-job-1" in result.output and "test-job-120" in result.output
    ), f"expected data not found in output: {result.output}"
