import os
from unittest import mock

from click.testing import Result
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import cli_assert_equal

from functional.run import util


def test_write_directory_default():
  runner = CliEntryBasedTestRunner()
  result: Result = runner.invoke(
      ["run", util.job_path("write-directory"), "--arguments",
       '{"expected_directory_string" : "/var/tmp"}'])
  cli_assert_equal(0, result)


@mock.patch.dict(os.environ, {"VDK_WRITE_DIRECTORY": "TEST_VALUE_STRING"})
def test_write_directory_non_default():
  runner = CliEntryBasedTestRunner()
  result: Result = runner.invoke(
      ["run", util.job_path("write-directory"), "--arguments",
       '{"expected_directory_string" : "TEST_VALUE_STRING"}'])
  cli_assert_equal(0, result)
