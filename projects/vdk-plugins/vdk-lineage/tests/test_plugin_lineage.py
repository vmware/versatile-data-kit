# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.plugin.lineage import plugin_lineage
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory
from werkzeug import Request
from werkzeug import Response


def test_job_lineage_disabled(tmpdir):
    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin, plugin_lineage)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )

        cli_assert_equal(0, result)


def test_job_lineage(tmpdir, httpserver: PluginHTTPServer):
    api_url = httpserver.url_for("")
    # api_url = "http://localhost:5002"

    sent_data = []

    def handler(r: Request):
        sent_data.append(json.loads(r.data))
        return Response(status=200)

    httpserver.expect_request(
        uri="/api/v1/lineage", method="POST"
    ).respond_with_handler(handler)

    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
            "VDK_OPENLINEAGE_URL": api_url,
        },
    ):
        runner = CliEntryBasedTestRunner(sqlite_plugin, plugin_lineage)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )

        cli_assert_equal(0, result)
        assert len(sent_data) == 7
