# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json

import httpretty
from click.testing import Result
from vdk.plugin.singer import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


@httpretty.activate
def test_singer_command():
    httpretty.register_uri(
        httpretty.GET,
        "https://pypi.org/simple/",
        body='{"meta":{"api-version":"1.1"},'
        '"projects":[{"name":"sqlite"},{"name":"tap-postgres"},{"name":"requests"},{"name":"tap-rest-api"}]}',
    )

    runner = CliEntryBasedTestRunner(plugin_entry)

    result: Result = runner.invoke(["singer", "--list-taps", "-o", "json"])

    cli_assert_equal(0, result)

    assert json.loads(result.stdout) == [
        {"name": "tap-postgres", "url": "https://pypi.org/project/tap-postgres"},
        {"name": "tap-rest-api", "url": "https://pypi.org/project/tap-rest-api"},
    ]
