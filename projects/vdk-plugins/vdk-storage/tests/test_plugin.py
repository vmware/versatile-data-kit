# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
from unittest import mock

from click.testing import Result
from vdk.plugin.storage import plugin_entry
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory

"""
This is a sample test file showing a recommended way to test new plugins.
A good way to test a new plugin is how it would be used in the command that it extends.
"""


def test_dummy():
    with mock.patch.dict(
        os.environ,
        {
            # mock the vdk configuration needed for our test
        },
    ):
        # CliEntryBasedTestRunner (provided by vdk-test-utils) gives a away to simulate vdk command
        # and mock large parts of it - e.g passed our own plugins
        runner = CliEntryBasedTestRunner(plugin_entry)

        result: Result = runner.invoke(
            ["run", jobs_path_from_caller_directory("job-using-a-plugin")]
        )
        cli_assert_equal(0, result)
