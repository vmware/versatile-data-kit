# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import json

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus.vdk import test_utils
from taurus.vdk.control.command_groups.job.execute import execute
from werkzeug import Response

test_utils.disable_vdk_authentication()

os.environ["VDK_ACKNOWLEDGE_USE_OF_EXPERIMENTAL_EXECUTE_API"] = "yes"


def test_execute(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
        method="POST",
    ).respond_with_response(
        Response(
            status=200,
            headers=dict(
                Location=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/foo"
            ),
        )
    )

    runner = CliRunner()
    result = runner.invoke(
        execute, ["-n", job_name, "-t", team_name, "--start", "-u", rest_api_url]
    )

    assert result.exit_code == 0, (
        f"result exit code is not 0, result output: {result.output}, "
        f"result.exception: {result.exception}"
    )


def test_execute_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(execute, ["-n", "job_name", "-t", "team_name"])

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_execute_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(execute, ["-n", "job_name", "-t", "team_name", "-u", ""])

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_execute_start_output_text(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
        method="POST",
    ).respond_with_response(
        Response(
            status=200,
            headers=dict(
                Location=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/foo"
            ),
        )
    )

    runner = CliRunner()
    result = runner.invoke(
        execute, ["-n", job_name, "-t", team_name, "--start", "-u", rest_api_url]
    )

    assert f"-n {job_name}" in result.output
    assert f"-t {team_name}" in result.output


def test_execute_start_output_json(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
        method="POST",
    ).respond_with_response(
        Response(
            status=200,
            headers=dict(
                Location=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/foo"
            ),
        )
    )

    runner = CliRunner()
    result = runner.invoke(
        execute, ["-n", job_name, "-t", team_name, "--start", "-u", rest_api_url, "-o", "json"]
    )
    json_output = json.loads(result.output)

    assert job_name == json_output.get("job_name")
    assert team_name == json_output.get("team")
    
def test_execute_with_exception(httpserver: PluginHTTPServer, tmpdir:LocalPath):
    runner = CliRunner()
    result = runner.invoke(execute, ["--start", "-n", "job_name", "-t", "team_name", "-u", "localhost"])
    
    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output
