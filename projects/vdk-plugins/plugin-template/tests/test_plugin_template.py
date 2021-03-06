# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.plugin_template import plugin_template
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_test_job_path

"""
This is a sample test file showing a recommended way to test new plugins.
A good way to test a new plugin is how it would be used in the command that it extends.
"""


def job_path(job_name: str):
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))), job_name
    )


def test_http_ingestion():
    with mock.patch.dict(
        os.environ,
        {
            # mock the vdk configuration needed for our test
        },
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_template)

        result: Result = runner.invoke(["run", job_path("job-using-a-plugin")])
        cli_assert_equal(0, result)
