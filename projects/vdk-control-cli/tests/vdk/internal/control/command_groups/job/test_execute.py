# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest.mock import patch

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobExecution
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.execute import execute
from werkzeug import Response

test_utils.disable_vdk_authentication()


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


def test_cancel(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"
    execution_id = "test-execution"

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}",
        method="DELETE",
    ).respond_with_response(Response(status=200, headers={}))

    runner = CliRunner()
    result = runner.invoke(
        execute,
        [
            "-n",
            job_name,
            "-t",
            team_name,
            "-i",
            execution_id,
            "--cancel",
            "-u",
            rest_api_url,
        ],
    )

    assert result.exit_code == 0, (
        f"result exit code is not 0, result output: {result.output}, "
        f"result.exception: {result.exception}"
    )


def test_execute_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(execute, ["-n", "job_name", "-t", "team_name", "-u", ""])

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
        execute,
        ["-n", job_name, "-t", team_name, "--start", "-u", rest_api_url, "-o", "json"],
    )
    json_output = json.loads(result.output)

    assert job_name == json_output.get("job_name")
    assert team_name == json_output.get("team")


def test_execute_with_exception(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(
        execute, ["--start", "-n", "job_name", "-t", "team_name", "-u", "localhost"]
    )

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_execute_no_execution_id(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"

    execution: DataJobExecution = DataJobExecution(
        id="1",
        job_name=job_name,
        logs_url="",
        deployment=DataJobDeployment(),
        start_time="2021-09-24T14:14:03.922Z",
    )
    older_execution = DataJobExecution(
        id="2",
        job_name=job_name,
        logs_url="",
        deployment=DataJobDeployment(),
        start_time="2020-09-24T14:14:03.922Z",
    )

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions",
        method="GET",
    ).respond_with_json(
        [older_execution.to_dict(), execution.to_dict(), older_execution.to_dict()]
    )

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/1/logs",
        method="GET",
    ).respond_with_json({"logs": "We are the logs! We are awesome!"})

    runner = CliRunner()
    result = runner.invoke(
        execute,
        ["-n", job_name, "-t", team_name, "--logs", "-u", rest_api_url],
    )
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == "We are the logs! We are awesome!".strip()


def test_execute_logs_using_api(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"
    id = "1"

    execution: DataJobExecution = DataJobExecution(
        id=id, job_name=job_name, logs_url="", deployment=DataJobDeployment()
    )

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/1",
        method="GET",
    ).respond_with_json(execution.to_dict())

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/1/logs",
        method="GET",
    ).respond_with_json({"logs": "We are the logs! We are awesome!"})

    runner = CliRunner()
    result = runner.invoke(
        execute,
        ["-n", job_name, "-t", team_name, "-i", id, "--logs", "-u", rest_api_url],
    )
    test_utils.assert_click_status(result, 0)
    assert result.output.strip() == "We are the logs! We are awesome!".strip()


def test_execute_logs_with_external_log_url(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"
    id = "1"

    execution: DataJobExecution = DataJobExecution(
        id=id,
        job_name=job_name,
        logs_url="http://external-service-job-logs",
        deployment=DataJobDeployment(),
    )

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/1",
        method="GET",
    ).respond_with_json(execution.to_dict())

    with patch("webbrowser.open") as mock_browser_open:
        mock_browser_open.return_value = False

        runner = CliRunner()
        result = runner.invoke(
            execute,
            ["-n", job_name, "-t", team_name, "-i", id, "--logs", "-u", rest_api_url],
        )
        test_utils.assert_click_status(result, 0)
        mock_browser_open.assert_called_once_with("http://external-service-job-logs")


def test_execute_start_extra_arguments_invalid_json(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
        method="POST",
    )

    runner = CliRunner()
    result = runner.invoke(
        execute,
        [
            "-n",
            job_name,
            "-t",
            team_name,
            "--start",
            "-u",
            rest_api_url,
            "--arguments",
            '{key1": "value1", "key2": "value2"}',
        ],
    )

    assert (
        result.exit_code == 2
    ), f"Result exit code not 2. result output {result.output}, exc: {result.exc_info}"
    assert "Failed to validate job arguments" in result.output
    assert "what" and "why" in result.output
    assert "Make sure provided --arguments is a valid JSON string." in result.output


def test_execute_start_extra_arguments(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    team_name = "test-team"
    job_name = "test-job"
    arguments = '{"key1": "value1", "key2": "value2"}'

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/production/executions",
        method="POST",
        json=json.loads(
            '{"args": {"key1": "value1", "key2": "value2"}, "started_by": "vdk-control-cli"}'
        ),
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
        execute,
        [
            "-n",
            job_name,
            "-t",
            team_name,
            "--start",
            "-u",
            rest_api_url,
            "--arguments",
            arguments,
        ],
    )
    assert (
        result.exit_code == 0
    ), f"Result exit code not 0. result output {result.output}, exc: {result.exc_info}"
