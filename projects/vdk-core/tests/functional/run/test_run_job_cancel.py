# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest.mock
from unittest.mock import MagicMock
from unittest.mock import patch

from click.testing import Result
from functional.run import util
from vdk.internal.core import errors
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


class TestCancellation(unittest.TestCase):
    @patch(
        "vdk.internal.builtin_plugins.termination_message.writer.TerminationMessageWriterPlugin"
        + ".write_termination_message"
    )
    def test_run(self, patched_writer: MagicMock):
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

        # clear recorded errors before invoking run since other tests might leave a dirty state
        errors.clear_intermediate_errors()

        result: Result = test_runner.invoke(["run", util.job_path("cancel-job")])

        # Check the writer plugin wasn't called with user or platform errors.
        # 1st param is overall blamee, should be None.
        # 2nd parm is overall user error in this case it's empty string which is a falsy value.
        # 3rd param is context.configuration and can be ignored for this test.
        patched_writer.assert_called_once_with(None, "", unittest.mock.ANY)
        assert "Step Cancel 1." in result.output
        assert "Step Cancel 2." in result.output
        assert "Step Cancel 3." not in result.output
        assert (
            "Job/template execution was skipped from job/template step code."
            in result.output
        )
        cli_assert_equal(0, result)
