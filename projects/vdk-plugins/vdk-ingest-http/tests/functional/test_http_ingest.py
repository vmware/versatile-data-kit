# Copyright 2023-2026 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from pytest_httpserver.pytest_plugin import PluginHTTPServer
from vdk.plugin.ingest_http import ingest_http_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path
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
            "VDK_INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD": "1000",
        },
    ):
        # create table first, as the ingestion fails otherwise
        runner = CliEntryBasedTestRunner(ingest_http_plugin)

        result: Result = runner.invoke(["run", job_path("ingest-job")])
        cli_assert_equal(0, result)

        # The number of batches depends on sys.getsizeof() which varies between Python versions.
        # We calculate the expected number of batches dynamically based on the exact same logic
        # used in ingester_base.py to chunk the payload.
        import sys

        expected_batches = 0
        current_size = 0
        for i in range(100):
            row_dict = {"index": i, "next": i + 1, "word": "hi", "@table": "test"}
            row_size = sys.getsizeof(str(row_dict))
            if current_size + row_size > 1000:
                expected_batches += 1
                current_size = 0
            current_size += row_size
        if current_size > 0:
            expected_batches += 1

        assert len(httpserver.log) == expected_batches


def test_ingestion_retry(httpserver: PluginHTTPServer):
    httpserver.expect_request(uri="/ingest").respond_with_response(Response(status=502))

    with mock.patch.dict(
        os.environ,
        {
            "VDK_INGEST_METHOD_DEFAULT": "http",
            "VDK_INGEST_TARGET_DEFAULT": httpserver.url_for("/ingest"),
            "VDK_INGEST_OVER_HTTP_RETRY_TOTAL": "3",
            "VDK_INGEST_OVER_HTTP_RETRY_BACKOFF_FACTOR": "0.01",  # very short retry backoff interval
            "VDK_INGEST_OVER_HTTP_RETRY_STATUS_FORCELIST": "502",
            "VDK_INGESTER_PAYLOAD_SIZE_BYTES_THRESHOLD": "20000",
        },
    ):
        runner = CliEntryBasedTestRunner(ingest_http_plugin)

        result: Result = runner.invoke(["run", job_path("ingest-job")])
        cli_assert_equal(1, result)

        # one "regular" request + 3 retries
        assert len(httpserver.log) == 4
