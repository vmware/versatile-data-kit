# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import asyncio
import os
import pathlib
import unittest
from unittest import mock

import click
import pytest
from click.testing import Result
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.kerberos import kerberos_plugin
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_funcs import get_caller_directory
from vdk.plugin.test_utils.util_funcs import jobs_path_from_caller_directory


@click.command("my-echo")
@click.argument("value")
def my_echo(value):
    click.echo(value)


class DummyCmdPlugin:
    @staticmethod
    @hookimpl(tryfirst=True)
    def vdk_command_line(root_command: click.Group) -> None:
        root_command.add_command(my_echo)


@pytest.mark.usefixtures("kerberos_service")
class TestKerberosAuthentication(unittest.TestCase):
    def setUp(self) -> None:
        self.__runner = CliEntryBasedTestRunner(kerberos_plugin, DummyCmdPlugin())

    def test_no_authentication(self):
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_LOG_EXECUTION_RESULT": "True",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            assert '"status": "success"' in result.output
            cli_assert_equal(0, result)

    def test_invalid_authentication_mode(self):
        with mock.patch.dict(
            os.environ,
            {"VDK_KRB_AUTH": "invalid", "VDK_KRB_AUTH_FAIL_FAST": "true"},
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            assert "VDK_KRB_AUTH has invalid value" in str(result.exception)
            cli_assert_equal(1, result)

    def test_kinit_authentication(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_LOG_EXECUTION_RESULT": "True",
            },
        ):
            result: Result = self.__runner.invoke(
                ["run", jobs_path_from_caller_directory("test-job")]
            )

            cli_assert_equal(0, result)
            assert '"status": "success"' in result.output

    def test_kinit_authentication_cli_command_no_auth(self):
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
            },
        ):
            result: Result = self.__runner.invoke(["my-echo", "hi"])

            cli_assert_equal(0, result)

    def test_kinit_authentication_cli_command(self):
        data_job_path = jobs_path_from_caller_directory("test-job")
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KEYTAB_REALM": "EXAMPLE.COM",
                "VDK_KERBEROS_KDC_HOST": "localhost",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FOLDER": str(pathlib.Path(data_job_path).parent),
                "VDK_KEYTAB_FILENAME": "test-job.keytab",
                "VDK_KEYTAB_PRINCIPAL": "pa__view_test-job",
            },
        ):
            result: Result = self.__runner.invoke(["my-echo", "hi"])

            cli_assert_equal(0, result)

    def test_minikerberos_authentication_cli_command(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KEYTAB_REALM": "EXAMPLE.COM",
                "VDK_KERBEROS_KDC_HOST": "localhost",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FOLDER": str(get_caller_directory().joinpath("jobs")),
                "VDK_KEYTAB_FILENAME": "test-job.keytab",
                "VDK_KEYTAB_PRINCIPAL": "pa__view_test-job",
            },
        ):
            result: Result = self.__runner.invoke(["my-echo", "hi"])

            cli_assert_equal(0, result)

    def test_minikerberos_authentication_cli_command_no_keytab_file(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_PRINCIPAL": "pa__view_test-job",
            },
        ):
            result: Result = self.__runner.invoke(["my-echo", "hi"])

            cli_assert_equal(0, result)

    def test_kinit_authentication_with_wrong_credentials(self):
        # Try to authenticate a data job using a keytab for a different principal.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath(
                        "different_principal.keytab"
                    )
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "kinit returned exitcode 1" in str(result.exception)
            cli_assert_equal(1, result)

    def test_kinit_authentication_error_fail_fast_is_false(self):
        # Try to authenticate a data job using a missing keytab.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB_AUTH_FAIL_FAST": "false",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath("non_existent.keytab")
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])
            cli_assert_equal(0, result)

    def test_kinit_authentication_with_missing_keytab(self):
        # Try to authenticate a data job using a missing keytab.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "kinit",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FOLDER": str(pathlib.Path(data_job_path).parent),
                "VDK_KEYTAB_FILENAME": "non_existent.keytab",
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Cannot locate keytab file" in str(result.exception)
            cli_assert_equal(1, result)

    def test_minikerberos_authentication(self):
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KEYTAB_REALM": "EXAMPLE.COM",
                "VDK_KERBEROS_KDC_HOST": "localhost",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_LOG_EXECUTION_RESULT": "True",
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
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FOLDER": str(pathlib.Path(data_job_path).parent),
                "VDK_KEYTAB_FILENAME": "different_principal.keytab",
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Client not found in Kerberos database" in str(result.exception)
            cli_assert_equal(1, result)

    def test_minikerberos_authentication_with_missing_keytab(self):
        # Try to authenticate a data job using a missing keytab.
        krb5_conf_filename = str(get_caller_directory().joinpath("krb5.conf"))
        data_job_path = jobs_path_from_caller_directory("test-job")
        with mock.patch.dict(
            os.environ,
            {
                "VDK_KRB_AUTH": "minikerberos",
                "VDK_KRB_AUTH_FAIL_FAST": "true",
                "VDK_KRB5_CONF_FILENAME": krb5_conf_filename,
                "VDK_KEYTAB_FILENAME": str(
                    pathlib.Path(data_job_path).parent.joinpath("non_existent.keytab")
                ),
            },
        ):
            result: Result = self.__runner.invoke(["run", data_job_path])

            assert "Cannot locate keytab file" in str(result.exception)
            cli_assert_equal(1, result)

    def test_minikerberos_authentication_within_asyncio_event_loop(self):
        async def test_coroutine():
            self.test_minikerberos_authentication()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_coroutine())
