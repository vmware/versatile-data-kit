# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
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

        assert '"status": "success"' in result.output
        cli_assert_equal(0, result)

    def test_invalid_authentication_mode(self):
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "invalid",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            assert "VDK_KRB_AUTH has invalid value" in result.output
            cli_assert_equal(1, result)

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

            assert '"status": "success"' in result.output
            cli_assert_equal(0, result)

    def test_kinit_authentication_with_wrong_credentials(self):
        # Try to authenticate a data job using a keytab for a different principal.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath(
                        "different_principal.keytab"
                    )
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "kinit returned exitcode 1" in result.output
            cli_assert_equal(1, result)

    def test_kinit_authentication_with_missing_keytab(self):
        # Try to authenticate a data job using a missing keytab.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath("non_existent.keytab")
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Cannot locate keytab file" in result.output
            cli_assert_equal(1, result)

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

            assert '"status": "success"' in result.output
            cli_assert_equal(0, result)

    def test_minikerberos_authentication_with_wrong_credentials(self):
        # Try to authenticate a data job using a keytab for a different principal.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath(
                        "different_principal.keytab"
                    )
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Client not found in Kerberos database" in result.output
            cli_assert_equal(1, result)

    def test_minikerberos_authentication_with_missing_keytab(self):
        # Try to authenticate a data job using a missing keytab.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath("non_existent.keytab")
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Cannot locate keytab file" in result.output
            cli_assert_equal(1, result)
