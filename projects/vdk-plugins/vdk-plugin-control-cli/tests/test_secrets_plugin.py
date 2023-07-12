# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.plugin.control_cli_plugin import secrets_plugin
from vdk.plugin.control_cli_plugin import vdk_plugin_control_cli
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Request
from werkzeug import Response


def test_secrets_plugin(httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    secrets_data = {"original": 1}

    httpserver.expect_request(
        method="GET",
        uri=f"/data-jobs/for-team/test-team/jobs/secrets-job/deployments/TODO/secrets",
    ).respond_with_handler(
        lambda r: Response(status=200, response=json.dumps(secrets_data, indent=4))
    )

    def update_secrets_data(req: Request):
        secrets_data.clear()
        secrets_data.update(req.get_json())
        return Response(status=200)

    httpserver.expect_request(
        method="PUT",
        uri=f"/data-jobs/for-team/test-team/jobs/secrets-job/deployments/TODO/secrets",
    ).respond_with_handler(update_secrets_data)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_SERVICE_REST_API_URL": api_url,
            "VDK_secrets_DEFAULT_TYPE": "control-service",
        },
    ):
        runner = CliEntryBasedTestRunner(vdk_plugin_control_cli, secrets_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("secrets-job")]
        )
        cli_assert_equal(0, result)
        assert secrets_data == {"original": 1, "new": 2}


def test_secrets_plugin_no_url_configured():
    with mock.patch.dict(
        os.environ,
        {
            "VDK_secrets_DEFAULT_TYPE": "control-service",
        },
    ):
        runner = CliEntryBasedTestRunner(vdk_plugin_control_cli, secrets_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("simple-job")]
        )
        # job that do not use secrets should succeed
        cli_assert_equal(0, result)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("secrets-job")]
        )
        # but jobs that do use secrets should fail.
        cli_assert_equal(1, result)
