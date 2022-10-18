# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock
from unittest.mock import patch

from click.testing import Result
from functional.run import util
from vdk.internal.core import errors
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


@patch(
    "vdk.internal.plugin.plugin.PluginRegistry.load_plugins_from_setuptools_entrypoints",
    side_effect=ImportError("Test import error."),
)
def test_run(patched_load: MagicMock):
    """
    This test simulates a scenario where a user imports a library that
    has a clash with vdk internal imports. We want to check that the
    exception is handled by vdk logic and exit status is not 0.
    :param patched_load: the patched method that throws ImportError
    :return:
    """
    test_runner = CliEntryBasedTestRunner()
    errors.clear_intermediate_errors()
    result: Result = test_runner.invoke(["run", util.job_path("cancel-job")])
    cli_assert_equal(1, result)
