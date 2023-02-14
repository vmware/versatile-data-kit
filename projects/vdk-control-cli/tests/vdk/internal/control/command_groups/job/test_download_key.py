# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.download_key import download_key
from werkzeug import Response

test_utils.disable_vdk_authentication()


def test_download_key(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    temp_dir = tmpdir.mkdir("key")

    data = b"data"
    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/keytab", method="GET"
    ).respond_with_data(data)

    runner = CliRunner()
    result = runner.invoke(
        download_key,
        ["-n", "test-job", "-t", "test-team", "-u", rest_api_url, "-p", temp_dir],
    )

    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"
    expected_file_path = os.path.join(temp_dir, "test-job.keytab")
    with open(expected_file_path, "rb") as myfile:
        actual_data = myfile.read()
        assert actual_data == data


def test_download_key_error(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    temp_dir = tmpdir.mkdir("key")

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/keytab"
    ).respond_with_response(Response(status=510))

    runner = CliRunner()
    result = runner.invoke(
        download_key,
        ["-n", "test-job", "-t", "test-team", "-u", rest_api_url, "-p", temp_dir],
    )

    assert result.exit_code != 0
    # check error is printed to user (all errors have what/why/... format)
    assert "what" in result.output and "why" in result.output


def test_download_key_without_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    temp_dir = tmpdir.mkdir("key")

    runner = CliRunner()
    result = runner.invoke(
        download_key, ["-n", "test-job", "-t", "test-team", "-p", temp_dir]
    )

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output


def test_download_key_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    temp_dir = tmpdir.mkdir("key")

    runner = CliRunner()
    result = runner.invoke(
        download_key, ["-n", "test-job", "-t", "test-team", "-p", temp_dir, "-u", ""]
    )

    assert (
        result.exit_code == 2
    ), f"result exit code is not 2, result output: {result.output}, exc: {result.exc_info}"
    assert "what" in result.output and "why" in result.output
