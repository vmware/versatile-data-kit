# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest import mock

import pytest
from click.testing import Result
from vdk.plugin.kerberos import kerberos_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_caller_directory
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@pytest.mark.usefixtures("kerberos_service")
class TemplateRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(kerberos_plugin)

    def test_no_authentication(self):
        result: Result = self.__runner.invoke(
            ["run", jobs_path_from_caller_directory("test-job")]
        )

        cli_assert_equal(0, result)

    def test_kinit_authentication(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            cli_assert_equal(0, result)

    def test_minikerberos_authentication(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KEYTAB_REALM": "EXAMPLE.COM",
                "VDK_KERBEROS_KDC_HOST": "localhost",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            cli_assert_equal(0, result)
