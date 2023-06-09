# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import traceback
from unittest import mock

from click.testing import CliRunner
from py._path.local import LocalPath
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.internal import test_utils
from vdk.internal.control.command_groups.job.create import create
from vdk.internal.test_utils import assert_click_status
from werkzeug import Response

# TODO: using class pytest cannot find the tests for some reason ...?!
# class CreateCommandTest
# https://pytest-httpserver.readthedocs.io/en/latest/
# https://docs.pytest.org/en/2.7.3/tmpdir.html

test_utils.disable_vdk_authentication()


def test_create_job(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    job_dir = os.path.join(jobs_dir, job_name)
    assert_click_status(result, 0)
    assert os.path.isdir(job_dir)
    assert os.path.isfile(os.path.join(job_dir, "config.ini"))
    assert os.path.isfile(os.path.join(jobs_dir, f"{job_name}.keytab"))


def test_create_job_prompts(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-u", rest_api_url], input=f"{job_name}\n{team_name}\n{jobs_dir}"
    )

    job_dir = os.path.join(jobs_dir, job_name)
    assert_click_status(result, 0)
    assert os.path.isdir(job_dir)
    assert os.path.isfile(os.path.join(job_dir, "config.ini"))
    assert os.path.isfile(os.path.join(jobs_dir, f"{job_name}.keytab"))


def test_create_job_configurable_sample_job(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )
    sample_dir = tmpdir.mkdir("sample")
    sample_dir.join("foo").write("")
    sample_dir.join("config.ini").write("")

    with mock.patch.dict(
        os.environ, {"VDK_CONTROL_SAMPLE_JOB_DIRECTORY": str(sample_dir)}
    ):
        runner = CliRunner()
        result = runner.invoke(
            create,
            ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir],
        )

        job_dir = os.path.join(jobs_dir, job_name)
        assert_click_status(result, 0)
        assert os.path.isdir(job_dir)
        # foo file exists only in our sample job
        assert os.path.isfile(os.path.join(job_dir, "foo"))


def test_create_job_configurable_sample_job_module(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    import click
    from vdk.internal.control.utils import cli_utils
    from vdk.internal.control.command_groups.job.create import JobCreate

    from resources import sample_job_module

    @click.command()
    @click.option("-n", "--name", type=click.STRING)
    @click.option("-t", "--team", type=click.STRING)
    @click.option("-p", "--path", type=click.Path(exists=False, resolve_path=True))
    @cli_utils.rest_api_url_option()
    def create_new_sample_job_module(
        name: str,
        team: str,
        path: str,
        rest_api_url: str,
    ) -> None:
        cmd = JobCreate(rest_api_url)

        name = cli_utils.get_or_prompt("Job Name", name)
        team = cli_utils.get_or_prompt("Job Team", team)

        path = cli_utils.get_or_prompt(
            "Path to where sample data job will be created locally",
            path,
            os.path.abspath("."),
        )
        cmd.validate_job_path(path, name)

        cmd.create_job(name, team, path, False, True, sample_job_module)
        pass

    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )
    sample_dir = tmpdir.mkdir("sample")
    sample_dir.join("foo").write("")
    sample_dir.join("config.ini").write("")

    runner = CliRunner()
    result = runner.invoke(
        create_new_sample_job_module,
        ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir],
    )

    job_dir = os.path.join(jobs_dir, job_name)
    assert_click_status(result, 0)
    assert os.path.isdir(job_dir)
    # foo file exists only in our sample job
    assert os.path.isfile(os.path.join(job_dir, "foo"))


def test_create_job_bad_format(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 400, 400, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert_click_status(result, 2)


def test_create_job_already_exists(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 409, 409, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert_click_status(result, 0)


def test_create_job_target_dir_exists(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )
    job_dir = jobs_dir.join(job_name)
    os.mkdir(job_dir)

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert_click_status(result, 2)
    # TODO: verify user gets some appropriate message and we fail for right reason (and not a bug in test)
    # assert result.output != ''


def test_create_parent_path_not_exists(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 200, job_name, team_name
    )
    job_dir = jobs_dir.join(job_name)
    os.mkdir(job_dir)

    runner = CliRunner()
    result = runner.invoke(
        create,
        [
            "-n",
            job_name,
            "-t",
            team_name,
            "-u",
            rest_api_url,
            "-p",
            "should-not-exists-at-all",
        ],
    )

    assert_click_status(result, 2)


def test_create_job_unable_to_download_keytab(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 200, 400, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    job_dir = os.path.join(jobs_dir, job_name)
    assert_click_status(result, 0)
    assert os.path.isdir(job_dir)
    assert os.path.isfile(os.path.join(job_dir, "config.ini"))
    assert not os.path.exists(os.path.join(jobs_dir, f"{job_name}.keytab"))


def test_create_without_url_only_local_detected(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    jobs_dir = tmpdir.mkdir("jobs")

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", "job-name", "-t", "team_name", "-p", jobs_dir, "-u", ""]
    )

    assert_click_status(result, 0)


def test_create_without_url_cloud_flag(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    jobs_dir = tmpdir.mkdir("jobs")

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", "job-name", "-t", "team_name", "-p", jobs_dir, "--cloud"]
    )

    assert_click_status(result, 2)


def test_create_only_local_flag(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "test-job"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 500, 500, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create,
        [
            "-n",
            "job-name",
            "-t",
            "team_name",
            "-p",
            jobs_dir,
            "-u",
            rest_api_url,
            "--local",
        ],
    )

    # created only locally would not try to contact REST API so it should succeeds.
    assert_click_status(result, 0)


def test_create_with_empty_url(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    jobs_dir = tmpdir.mkdir("jobs")

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", "job-name", "-t", "team_name", "-p", jobs_dir, "-u", ""]
    )

    assert_click_status(result, 0)


def test_create_with_too_long_job_name(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "this-name-is-far-too-long-for-the-use-of-being-a-job-name-and-will-hopefully-cause-an-appropriate-error"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 409, 409, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert (
        result.exit_code != 0
        and "Job name length must be within 5 to 45 characters." in result.output
    )


def test_create_with_not_alphanum_job_name(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    team_name = "test-team"
    job_name = "this_%string^is!not;alphanumeric"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 409, 409, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert (
        result.exit_code != 0
        and "Job name must only contain alphanumerical symbols and dashes."
        in result.output
    )


def test_create_job_name_doesnt_begin_with_letter(
    httpserver: PluginHTTPServer, tmpdir: LocalPath
):
    team_name = "test-team"
    job_name = "1this-name-begins-with-a-number"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 409, 409, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert (
        result.exit_code != 0 and "Job name must begin with a letter." in result.output
    )


def test_create_job_name_not_lowercase(httpserver: PluginHTTPServer, tmpdir: LocalPath):
    team_name = "test-team"
    job_name = "This-Name-Is-Not-Lowercase"
    jobs_dir, rest_api_url = setup_create(
        httpserver, tmpdir, 409, 409, job_name, team_name
    )

    runner = CliRunner()
    result = runner.invoke(
        create, ["-n", job_name, "-t", team_name, "-u", rest_api_url, "-p", jobs_dir]
    )

    assert (
        result.exit_code != 0
        and "Job name must only contain lowercase symbols." in result.output
    )


def setup_create(
    httpserver: PluginHTTPServer,
    tmpdir: LocalPath,
    jobStatus: int,
    keytabStatus: int,
    job_name: str,
    team_name: str,
):
    # see model/apidefs/datajob-api/api.yaml for expected request/response
    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs", method="POST"
    ).respond_with_response(Response(status=jobStatus))
    httpserver.expect_request(
        uri=f"/data-jobs/for-team/{team_name}/jobs/{job_name}/keytab", method="GET"
    ).respond_with_response(Response(status=keytabStatus))
    rest_api_url = httpserver.url_for("")
    jobs_dir = tmpdir.mkdir("jobs")
    return jobs_dir, rest_api_url
