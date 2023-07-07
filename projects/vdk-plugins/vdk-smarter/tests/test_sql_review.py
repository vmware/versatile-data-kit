# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import re
from unittest import mock

import openai
from click.testing import Result
from pytest_httpserver import HTTPServer
from vdk.plugin.smarter import openai_plugin_entry
from vdk.plugin.sqlite import sqlite_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

# uses the pytest tmpdir fixture - https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture


def test_openai_review_plugin(tmpdir, httpserver: HTTPServer):
    # Mock OpenAI response
    review_comment = "This is a well written SQL query."
    httpserver.expect_oneshot_request(re.compile(r".*")).respond_with_json(
        {
            "id": "test",
            "model": "foo",
            "choices": [
                {
                    "text": " Here is the review: {'score': 4, 'review': '"
                    + review_comment
                    + "'}",
                }
            ],
        }
    )

    # Set the OpenAI endpoint to the httpserver's uri
    openai.api_base = httpserver.url_for("")

    with mock.patch.dict(
        os.environ,
        {
            "VDK_DB_DEFAULT_TYPE": "SQLITE",
            "VDK_SQLITE_FILE": str(tmpdir) + "vdk-sqlite.db",
            "VDK_OPENAI_REVIEW_ENABLED": "true",
            "VDK_OPENAI_MODEL": "foo",
        },
    ):
        runner = CliEntryBasedTestRunner(openai_plugin_entry, sqlite_plugin)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("sql-job")]
        )

        cli_assert_equal(0, result)
        cli_assert(review_comment in result.output, result)

        assert pathlib.Path("queries_reviews_report.md").exists()
        assert review_comment in pathlib.Path("queries_reviews_report.md").read_text()
