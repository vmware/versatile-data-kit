# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest

from click.testing import Result
from vdk.plugin.kerberos import kerberos_plugin
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


class TemplateRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(kerberos_plugin)

    def test_no_authentication(self):
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("test-job")]
        )

        assert result.exit_code == 0
