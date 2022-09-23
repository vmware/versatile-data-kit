# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from click.testing import Result
from functional.run import util
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_run():
    """
    Test that runs a sample data job consisting of 3 steps.
    Each step logs <Step 1,2> etc. However after the second step's log call
    the cancel_job_execution method is invoked which should cancel
    the job execution. Test checks:
    execution is canceled and final step isn't executed.
    proper exit code is set.
    proper message is logged confirming job was cancelled from cancel_job_execution() method.
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
