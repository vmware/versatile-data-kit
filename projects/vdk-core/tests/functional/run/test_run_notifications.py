# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
from email.message import Message
from random import randint
from unittest import mock

from click.testing import Result
from functional.run import util
from smtpdfix import SMTPDFix
from vdk.internal.core import errors
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import DB_TYPE_SQLITE_MEMORY
from vdk.plugin.test_utils.util_plugins import DecoratedSqLite3MemoryDbPlugin

os.environ["SMTPD_SSL_CERTS_PATH"] = "."


def __get_smtp_env(smtpd: SMTPDFix):
    # https://github.com/bebleo/smtpdfix#using
    env = {
        "VDK_NOTIFICATION_ENABLED": "true",
        "VDK_ENABLE_ATTEMPT_NOTIFICATIONS": "true",
        "VDK_NOTIFICATION_SMTP_HOST": smtpd.hostname,
        "VDK_NOTIFICATION_SMTP_PORT": str(smtpd.port),
        "VDK_NOTIFICATION_SMTP_LOGIN_USERNAME": "",
        "VDK_NOTIFICATION_SMTP_LOGIN_PASSWORD": "",
        "VDK_NOTIFICATION_SMTP_DEBUG_LEVEL": "2",
        "VDK_NOTIFICATION_SMTP_USE_TLS": "false",
        "VDK_NOTIFICATION_SENDER": "sender@unittest.test",
    }
    return env


def test_run_successfull():
    errors.resolvable_context().clear()

    port = randint(10000, 20000)
    host = "127.0.0.1"
    with SMTPDFix(host, port) as server:
        with mock.patch.dict(
            os.environ,
            {
                **__get_smtp_env(server),
                "VDK_NOTIFIED_ON_JOB_SUCCESS": "tester@unittest.test",
            },
        ):
            runner = CliEntryBasedTestRunner()

            result: Result = runner.invoke(["run", util.job_path("simple-job")])

            cli_assert_equal(0, result)

            assert len(server.messages) == 1
            message: Message = server.messages[0]
            assert "tester@unittest.test" == message.get("To")
            assert "simple-job" in message.get("Subject")


def test_run_successfull_notify_multiple_users():
    errors.resolvable_context().clear()
    port = randint(10000, 20000)
    host = "127.0.0.1"
    with SMTPDFix(host, port) as server:
        with mock.patch.dict(
            os.environ,
            {
                **__get_smtp_env(server),
                "VDK_NOTIFIED_ON_JOB_SUCCESS": "t1@unittest.test;t2@unittest.test;t3@unittest.test",
            },
        ):
            runner = CliEntryBasedTestRunner()

            result: Result = runner.invoke(["run", util.job_path("simple-job")])

            cli_assert_equal(0, result)

            assert len(server.messages) == 1
            message: Message = server.messages[0]
            assert "t1@unittest.test" in message.get("To")
            assert "t2@unittest.test" in message.get("To")
            assert "t3@unittest.test" in message.get("To")


@mock.patch.dict(os.environ, {"VDK_DB_DEFAULT_TYPE": DB_TYPE_SQLITE_MEMORY})
def test_run_query_failed_user_error_notification_sent():
    errors.resolvable_context().clear()
    db_plugin = DecoratedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    port = randint(10000, 20000)
    host = "127.0.0.1"
    with SMTPDFix(host, port) as server:
        with mock.patch.dict(
            os.environ,
            {
                **__get_smtp_env(server),
                "VDK_NOTIFIED_ON_JOB_FAILURE_USER_ERROR": "tester@unittest.test",
            },
        ):
            result: Result = runner.invoke(
                ["run", util.job_path("simple-create-insert-failed")]
            )

            cli_assert_equal(1, result)
            assert len(server.messages) == 1


@mock.patch.dict(os.environ, {"VDK_DB_DEFAULT_TYPE": DB_TYPE_SQLITE_MEMORY})
def test_run_query_failed_user_error_no_notification_configured():
    errors.resolvable_context().clear()
    db_plugin = DecoratedSqLite3MemoryDbPlugin()
    runner = CliEntryBasedTestRunner(db_plugin)

    port = randint(10000, 20000)
    host = "127.0.0.1"
    with SMTPDFix(host, port) as server:
        with mock.patch.dict(
            os.environ,
            {
                **__get_smtp_env(server),
                # our job will fail with user error but we have configure platform error
                # so we should NOT get mail
                "NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR": "tester@unittest.test",
            },
        ):
            result: Result = runner.invoke(
                ["run", util.job_path("simple-create-insert-failed")]
            )

            cli_assert_equal(1, result)
            assert len(server.messages) == 0
