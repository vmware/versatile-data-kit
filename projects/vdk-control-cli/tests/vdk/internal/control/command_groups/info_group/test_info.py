# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import List

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.info_group.info import info
from vdk.internal.test_utils import assert_click_status

test_utils.disable_vdk_authentication()


def get_data_job_query_response(jobs: List[Any]):
    return dict(data=dict(content=jobs, errors=[]))


def get_example_info_response():
    return {
        "api_version": "PipelinesControlService/1.6.855638094/v0.13-30-g23b0851 (root@vdk-cs-dep-6f88c4bff-rzbbl Linux/amd64/amd64)",
        "supported_python_versions": ["python3.7", "python3.8", "python3.9"],
    }


def test_info(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    response = get_example_info_response()

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/info"
    ).respond_with_json(response)

    runner = CliRunner()
    result = runner.invoke(info, ["-t", "test-team", "-u", rest_api_url])
    assert_click_status(result, 0)
    assert (
        "PipelinesControlService/1.6.855638094/v0.13-30-g23b0851" in result.output
        and "python3.7" in result.output
    ), f"expected data not found in output: {result.output} "


def test_info_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(info, ["-t", "test-team"])
    assert_click_status(result, 2)
    assert "what" in result.output and "why" in result.output
