# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.download_job import download_job
from werkzeug import Response

test_utils.disable_vdk_authentication()


def _read_file(file_path):
    with open(file_path, "rb") as job_archive_file:
        file_path_binary = job_archive_file.read()
        return file_path_binary


def test_download_source(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    temp_dir = tmpdir.mkdir("foo")

    test_job_zip = test_utils.find_test_resource("job-zip/test-job.zip")
    data = _read_file(test_job_zip)

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/sources", method="GET"
    ).respond_with_data(data)

    runner = CliRunner()
    result = runner.invoke(
        download_job,
        ["-n", "test-job", "-t", "test-team", "-u", rest_api_url, "-p", temp_dir],
    )

    assert (
        result.exit_code == 0
    ), f"result exit code is not 0, result output: {result.output}"
    expected_dir_job = os.path.join(temp_dir, "test-job")
    assert pathlib.Path(expected_dir_job).is_dir()
    assert pathlib.Path(expected_dir_job).joinpath("config.ini").is_file()


def test_download_source_dir_exists(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    temp_dir = tmpdir.mkdir("foo")
    os.mkdir(os.path.join(temp_dir, "test-job"))

    runner = CliRunner()
    result = runner.invoke(
        download_job,
        ["-n", "test-job", "-t", "test-team", "-u", rest_api_url, "-p", temp_dir],
    )

    assert (
        result.exit_code == 2
    ), f"result exit code is not 1, result output: {result.output}"
    # assert it failed for the right reason:
    assert "Directory with name test-job already exists" in result.output


def test_download_job_does_not_exist(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    rest_api_url = httpserver.url_for("")
    temp_dir = tmpdir.mkdir("foo")

    httpserver.expect_request(
        uri="/data-jobs/for-team/test-team/jobs/test-job/sources", method="GET"
    ).respond_with_response(Response(status=404))

    runner = CliRunner()
    result = runner.invoke(
        download_job,
        ["-n", "test-job", "-t", "test-team", "-u", rest_api_url, "-p", temp_dir],
    )

    test_utils.assert_click_status(result, 2)
    # assert the correct message is returned, when there is no data job for the
    # specified team
    assert "The requested resource cannot be found" in result.output
    # assert that vdk does not try cleaning up a non-existent archive
    assert "Cannot cleanup archive" not in result.output
