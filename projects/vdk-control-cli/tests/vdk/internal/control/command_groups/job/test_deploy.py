# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from json import JSONDecodeError
from typing import Tuple

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus_datajob_api import DataJob
from taurus_datajob_api import DataJobConfig
from taurus_datajob_api import DataJobVersion
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.deploy_cli import deploy
from vdk.internal.test_utils import find_test_resource
from werkzeug import Response

test_utils.disable_vdk_authentication()

DEPLOYMENT_ID = "production"


def test_deploy(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    _, deploy_args = prepare_new_deploy(httpserver)

    runner = CliRunner()
    result = runner.invoke(deploy, deploy_args)
    test_utils.assert_click_status(result, 0)

    test_job_path = find_test_resource("test-job")
    assert os.path.exists(f"{test_job_path}.zip") is False

    posted_data = json.loads(httpserver.log[3][0].data)
    assert posted_data["job_version"] is not None


def test_deploy_with_vdk_version_disable(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    _, deploy_args = prepare_new_deploy(httpserver)

    runner = CliRunner()
    result = runner.invoke(deploy, [*deploy_args, "-v", "version", "--disable"])
    test_utils.assert_click_status(result, 0)

    posted_data = json.loads(httpserver.log[3][0].data)
    assert posted_data["vdk_version"] == "version"
    assert posted_data["enabled"] == False
    assert posted_data["job_version"] is not None


def test_deploy_update_remove(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    job_version, deploy_args = prepare_new_deploy(httpserver)

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--update",
            *deploy_args,
            "-v",
            "version",
        ],
    )
    test_utils.assert_click_status(result, 0)

    result = runner.invoke(
        deploy,
        [
            "--remove",
            *deploy_args,
            "-v",
            "version",
        ],
    )
    test_utils.assert_click_status(result, 0)


def test_deploy_with_output_json(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    job_version, deploy_args = prepare_new_deploy(httpserver)

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            *deploy_args,
            "-o",
            "json",
        ],
    )
    test_utils.assert_click_status(result, 0)
    try:
        json_result = json.loads(result.output)
    except JSONDecodeError as error:
        assert False, f"failed to parse the response as a JSON object, error: {error}"
    assert json_result["job_name"] == "test-job"
    assert json_result["job_version"] == job_version.version_sha


def test_deploy_reason(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    mock_base_requests(httpserver)

    job_version = DataJobVersion(version_sha="17012900f60461778c01ab24728807e70a5f2c87")
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/sources",
        method="POST",
        headers={"Content-Type": "application/octet-stream"},
        query_string="reason=Example%20reason",
    ).respond_with_json(job_version.to_dict())

    test_job_path = find_test_resource("test-job")

    runner = CliRunner()

    result = runner.invoke(
        deploy,
        [
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-p",
            test_job_path,
            "-u",
            rest_api_url,
            "-r",
            "Example reason",
        ],
    )

    test_utils.assert_click_status(result, 0)


def test_deploy_enable_disable(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/test-team/jobs/test-job/deployments/{DEPLOYMENT_ID}",
        method="PATCH",
    ).respond_with_response(Response(status=200))

    runner = CliRunner()
    result = runner.invoke(
        deploy, ["--enable", "-n", "test-job", "-t", "test-team", "-u", rest_api_url]
    )
    test_utils.assert_click_status(result, 0)
    assert httpserver.log[0][0].data == b'{"enabled": true}'

    result = runner.invoke(
        deploy, ["--disable", "-n", "test-job", "-t", "test-team", "-u", rest_api_url]
    )
    test_utils.assert_click_status(result, 0)
    assert httpserver.log[1][0].data == b'{"enabled": false}'


def test_set_vdk_version(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/test-team/jobs/test-job/deployments/{DEPLOYMENT_ID}",
        method="PATCH",
    ).respond_with_response(Response(status=200))

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--update",
            "--vdk-version",
            "1.1.1",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
        ],
    )
    test_utils.assert_click_status(result, 0)
    assert httpserver.log[0][0].data == b'{"vdk_version": "1.1.1"}'


def test_update_job_version(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments",
        method="POST",
    ).respond_with_response(Response(status=202))

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--update",
            "--job-version",
            "1.1",
            "--disable",
            "--vdk-version",
            "2.2",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
        ],
    )
    # print(f"httpserver.log: {httpserver.log}")
    test_utils.assert_click_status(result, 0)
    assert (
        httpserver.log[0][0].data
        == b'{"vdk_version": "2.2", "job_version": "1.1", "enabled": false}'
    )


def test_update_miltiple(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri=f"/data-jobs/for-team/test-team/jobs/test-job/deployments/{DEPLOYMENT_ID}",
        method="PATCH",
    ).respond_with_response(Response(status=200))

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--update",
            "--vdk-version",
            "1.1.1",
            "--enable",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
        ],
    )
    test_utils.assert_click_status(result, 0)
    assert httpserver.log[0][0].data == b'{"vdk_version": "1.1.1", "enabled": true}'


def test_deploy_show(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    response = [
        {
            "enabled": False,
            "job_version": "11a403ba",
            "mode": "testing",
            "last_deployed_by": "user",
            "last_deployed_date": "2021-02-25T09:16:53.323Z",
        }
    ]
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(
        deploy, ["--show", "-n", "test-job", "-t", "test-team", "-u", rest_api_url]
    )
    test_utils.assert_click_status(result, 0)
    assert (
        "11a403ba" in result.output
    ), f"expected data not found in output: {result.output} "
    assert (
        "user" in result.output
    ), f"expected data not found in output: {result.output} "
    assert (
        "2021-02-25T09:16:53.323Z" in result.output
    ), f"expected data not found in output: {result.output} "


def test_deploy_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(deploy, ["--show", "-n", "test-job", "-t", "test-team"])

    test_utils.assert_click_status(result, 2)
    assert "what" in result.output and "why" in result.output


def test_deploy_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(
        deploy, ["--show", "-n", "test-job", "-t", "test-team", "-u", ""]
    )

    test_utils.assert_click_status(result, 2)
    assert "what" in result.output and "why" in result.output


def test_deploy_show_with_json_output(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    response = [
        {
            "enabled": False,
            "job_version": "11a403ba",
            "mode": "testing",
            "last_deployed_by": "user",
            "last_deployed_date": "2021-02-25T09:16:53.323Z",
        }
    ]
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--show",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
            "-o",
            "json",
        ],
    )
    test_utils.assert_click_status(result, 0)

    try:
        json_result = json.loads(result.output)
    except JSONDecodeError as error:
        assert False, f"failed to parse the response as a JSON object, error: {error}"
    assert isinstance(json_result, list)
    assert len(list(json_result)) == 1
    assert (
        list(json_result)[0]["job_version"] == "11a403ba"
    ), f"expected data not found in output: {result.output}"
    assert (
        list(json_result)[0]["last_deployed_by"] == "user"
    ), f"expected data not found in output: {result.output}"
    assert (
        list(json_result)[0]["last_deployed_date"] == "2021-02-25T09:16:53.323Z"
    ), f"expected data not found in output: {result.output}"


def test_deploy_show_with_json_output_and_no_deployments(httpserver: PluginHTTPServer):
    rest_api_url = httpserver.url_for("")

    response = None
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--show",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
            "-o",
            "json",
        ],
    )
    test_utils.assert_click_status(result, 0)

    try:
        json_result = json.loads(result.output)
    except JSONDecodeError as error:
        assert False, f"failed to parse the response as a JSON object, error: {error}"
    assert isinstance(
        json_result, list
    ), f"expected a list, got: {type(json_result)}, output: {result.output}"
    assert (
        len(list(json_result)) == 0
    ), f"expected an empty list, got: {json_result}, output: {result.output}"


def test_deploy_show_with_missing_output_and_no_deployments(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    rest_api_url = httpserver.url_for("")

    response = None
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(
        deploy, ["--show", "-n", "test-job", "-t", "test-team", "-u", rest_api_url]
    )
    test_utils.assert_click_status(result, 0)
    assert (
        "No Data." in result.output
    ), f"expected data not found in output: {result.output}"


def test_deploy_show_with_invalid_output(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    rest_api_url = httpserver.url_for("")

    runner = CliRunner()
    result = runner.invoke(
        deploy,
        [
            "--show",
            "-n",
            "test-job",
            "-t",
            "test-team",
            "-u",
            rest_api_url,
            "-o",
            "invalid",
        ],
    )
    test_utils.assert_click_status(result, 2)
    assert (
        "Error: Invalid value for '--output'" in result.output
    ), f"expected data not found in output: {result.output}"


def test_deploy_failed_team_validation(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    runner = CliRunner()
    test_job_path = find_test_resource("test-job")
    result = runner.invoke(
        deploy,
        [
            "-n",
            "test-job",
            "-t",
            "wrong_test-team",
            "-p",
            test_job_path,
            "-u",
            rest_api_url,
            "-r",
            "reason",
        ],
    )
    test_utils.assert_click_status(result, 2)
    assert "what" in result.output and "why" in result.output


def prepare_new_deploy(httpserver) -> Tuple[str, str]:
    rest_api_url = httpserver.url_for("")
    mock_base_requests(httpserver)
    job_version = DataJobVersion(version_sha="17012900f60461778c01ab24728807e70a5f2c87")
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/sources",
        method="POST",
        headers={"Content-Type": "application/octet-stream"},
        query_string="reason=reason",
    ).respond_with_json(job_version.to_dict())
    test_job_path = find_test_resource("test-job")

    open(f"{test_job_path}.zip", "w")

    assert os.path.exists(f"{test_job_path}.zip") is True

    deploy_args = [
        "-n",
        "test-job",
        "-t",
        "test-team",
        "-p",
        test_job_path,
        "-u",
        rest_api_url,
        "-r",
        "reason",
    ]

    return job_version, deploy_args


def mock_base_requests(httpserver):
    existing_job = DataJob(
        job_name="test-job", team="test-team", description="", config=DataJobConfig()
    )
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job", method="GET"
    ).respond_with_json(existing_job.to_dict())

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job", method="PUT"
    ).respond_with_response(Response(status=200))

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/deployments", method="POST"
    ).respond_with_response(Response(status=200))
    httpserver.expect_request(
        uri=f"/data-jobs/for-team/test-team/jobs/test-job/deployments/{DEPLOYMENT_ID}"
    ).respond_with_response(Response(status=200))
