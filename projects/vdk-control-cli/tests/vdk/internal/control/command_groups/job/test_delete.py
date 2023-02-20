# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.delete import delete
from werkzeug import Response


test_utils.disable_vdk_authentication()


def test_delete(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job", method="DELETE"
    ).respond_with_response(Response(status=200))

    runner = CliRunner()
    result = runner.invoke(
        delete, ["-n", "test-job", "-t", "test-team", "--yes", "-u", rest_api_url]
    )

    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"


def test_delete_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(delete, ["-n", "test-job", "-t", "test-team", "--yes"])

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_delete_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    runner = CliRunner()
    result = runner.invoke(
        delete, ["-n", "test-job", "-t", "test-team", "--yes", "-u", ""]
    )

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output
