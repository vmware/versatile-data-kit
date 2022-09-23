# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_run():
    """
    Test checks:
    template execution is canceled and all job steps are executed.
    proper exit code is set.
    proper message is logged confirming template was cancelled from cancel_job_execution() method.
    :return:
    """
    test_runner = CliEntryBasedTestRunner()

    result: Result = test_runner.invoke(["run", util.job_path("cancel-job")])

    assert "Step 1." in result.output
    assert "Step 2." in result.output
    assert "Step 3." not in result.output
    assert (
        "Job/template execution was cancelled from job/template step code."
        in result.output
    )
    cli_assert_equal(0, result)
