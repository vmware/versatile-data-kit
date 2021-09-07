# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from taurus.vdk import ingest_http_plugin
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner
from taurus.vdk.test_utils.util_funcs import get_test_job_path
from werkzeug import Response


def job_path(job_name: str):
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))), job_name
    )


def test_http_ingestion(httpserver: PluginHTTPServer):
    httpserver.expect_request(uri="/ingest").respond_with_response(Response(status=200))

    with mock.patch.dict(
        os.environ,
        {
            "VDK_INGEST_METHOD_DEFAULT": "http",
            "VDK_INGEST_TARGET_DEFAULT": httpserver.url_for("/ingest"),
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(ingest_http_plugin)

        result: Result = runner.invoke(["run", job_path("ingest-job")])
        cli_assert_equal(0, result)

        assert len(httpserver.log) == 100
