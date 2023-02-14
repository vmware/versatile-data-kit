# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import smtplib
import unittest
from collections import defaultdict
from email.mime.text import MIMEText
from typing import cast
from unittest.mock import patch

from vdk.internal.builtin_plugins.notification import notification_base
from vdk.internal.builtin_plugins.notification.notification_configuration import (
    SmtpConfiguration,
)
from vdk.internal.core.config import Configuration

job_log_url_template = (
    "https://test.log.com/explorer/?existingChartQuery=%7B%22query"
    "%22%3A%22{op_id}%22%2C%22startTimeMillis%22%3A{start_time_ms}%2C%22"
    "endTimeMillis%22%3A{end_time_ms}%2C%22fieldConstraints%22%3A%5B%7B%22"
    "internalName%22%3A%22text%22%2C%22operator%22%3A%22CONTAINS%22%2C%22value%22%3A%22vdk%22%7D%5D%7D"
)
cc = None
sender = "vdk@test.com"
smtp_cfg = SmtpConfiguration(
    cast(
        Configuration,
        defaultdict(
            lambda: None,
            NOTIFICATION_SMTP_HOST="smtp.test.com",
            NOTIFICATION_SMTP_PORT=25,
            NOTIFICATION_SMTP_DEBUG_LEVEL=1,
        ),
    )
)


class NotificationTest(unittest.TestCase):
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._email_address_exists"
    )
    def test_get_valid_recipients(self, mock_email_exists):
        mock_email_exists.side_effect = [True, False]
        valid_recipients = notification_base.EmailNotification(
            [" valid1@test.com ", "invalid1@test.com"], cc, smtp_cfg, sender
        )._get_valid_recipients()

        self.assertEqual(["valid1@test.com"], valid_recipients)

    @patch("vdk.internal.builtin_plugins.notification.notification_base.LoggingSMTP")
    def test_email_address_exists_valid_email(self, mock_smtp):
        mock_smtp.return_value.rcpt.return_value = (250,)
        email_notification = notification_base.EmailNotification(
            [], "", smtp_cfg, sender
        )
        self.assertEqual(
            True, email_notification._email_address_exists("valid@test.com")
        )
        mock_smtp.return_value.rcpt.return_value = (100,)
        self.assertEqual(
            False, email_notification._email_address_exists("invalid@test.com")
        )
        mock_smtp.return_value.helo.side_effect = smtplib.SMTPServerDisconnected()
        self.assertEqual(
            True, email_notification._email_address_exists("smtp raises exception")
        )

    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._get_valid_recipients"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._build_message"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._send_message"
    )
    def test_notify(
        self, mock_send_message, mock_build_message, mock_get_valid_recipients
    ):
        email_notification = notification_base.EmailNotification(
            [], cc, smtp_cfg, sender
        )
        msg = MIMEText("body", "html")
        msg["Subject"] = "subject"
        msg["From"] = "from@email"
        msg["To"] = "to@email"
        msg["Cc"] = "cc@email"
        mock_build_message.return_value = msg
        mock_get_valid_recipients.return_value = ["some@email"]

        email_notification.notify("", "")

        self.assertEqual(mock_get_valid_recipients.call_count, 1)
        self.assertEqual(mock_build_message.call_count, 1)
        call_args, _ = mock_send_message.call_args
        sent_message = call_args[0]
        self.assertEqual("to@email", sent_message["To"])
        self.assertEqual("from@email", sent_message["From"])
        self.assertEqual("subject", sent_message["Subject"])
        self.assertEqual("cc@email", sent_message["Cc"])
        self.assertEqual("body", sent_message.get_payload())
        self.assertEqual("text/html", sent_message.get_content_type())

    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._get_valid_recipients"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._build_message"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._send_message"
    )
    def test_notify_no_recipient_emails(
        self, mock_send_message, mock_build_message, mock_get_valid_recipients
    ):
        email_notification = notification_base.EmailNotification(
            [], cc, smtp_cfg, sender
        )
        mock_get_valid_recipients.return_value = []

        email_notification.notify("", "")

        self.assertEqual(mock_get_valid_recipients.call_count, 1)
        self.assertEqual(mock_build_message.call_count, 0)
        self.assertEqual(mock_send_message.call_count, 0)

    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._get_valid_cc"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._get_valid_recipients"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._build_message"
    )
    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.EmailNotification._send_message"
    )
    def test_notify_no_valid_emails(
        self,
        mock_send_message,
        mock_build_message,
        mock_get_valid_recipients,
        mock_get_valid_cc,
    ):
        mock_get_valid_cc.return_value = ["cc-email@test.com"]
        mock_get_valid_recipients.return_value = []

        email_notification = notification_base.EmailNotification(
            ["not-valid-email@test.com"], ["cc-email@test.com"], smtp_cfg, sender
        )

        email_notification.notify("", "no-valid-email-body")

        self.assertEqual(mock_get_valid_recipients.call_count, 1)
        self.assertEqual(mock_build_message.call_count, 1)
        self.assertEqual(mock_send_message.call_count, 1)

    @patch("vdk.internal.builtin_plugins.notification.notification_base.LoggingSMTP")
    def test_send_email_message(self, mock_smtp):
        msg = notification_base.EmailNotification(
            [], cc, smtp_cfg, sender
        )._build_message("subject", "message", "somebody@test.com")

        notification_base.EmailNotification(
            "somebody@test.com", cc, smtp_cfg, sender
        )._send_message(msg)

        mock_smtp.return_value.send_message.assert_called_once_with(msg)

    def test_build_message(self):
        msg = notification_base.EmailNotification(
            [], cc, smtp_cfg, sender="other@test.com"
        )._build_message("subject", "body", "somebody@test.com,else@test.com")

        self.assertEqual("other@test.com", msg["From"])
        self.assertEqual("somebody@test.com,else@test.com", msg["To"])
        self.assertEqual("", msg["Cc"])
        self.assertEqual("subject", msg["Subject"])
        self.assertEqual("body", msg.get_payload())
        self.assertEqual("text/html", msg.get_content_type())

    @patch("time.time", return_value=100000)
    def test_get_job_log_url(self, mock_time):
        expected_url = (
            "https://test.log.com/explorer/?existingChartQuery=%7B%22query%22%3A%22op_id%22%2C%22"
            "startTimeMillis%22%3A13600000%2C%22endTimeMillis%22%3A103600000"
            "%2C%22fieldConstraints%22%3A%5B%7B%22internalName%22%3A%22text%22%2C%22"
            "operator%22%3A%22CONTAINS%22%2C%22value%22%3A%22vdk%22%7D%5D%7D"
        )
        actual_url = notification_base.SuccessEmailNotificationMessageBuilder(
            "job_name", job_log_url_template
        )._get_job_log_url("op_id")

        self._assert_equal_str_without_whitespaces(expected_url, actual_url)

    def test_get_subject_success(self):
        actual_subject = notification_base.SuccessEmailNotificationMessageBuilder(
            "job_name", job_log_url_template
        )._get_subject("success", "run")
        expected_subject = "[success][data job run] job_name"

        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)

    def test_get_subject_failure(self):
        actual_subject = notification_base.SuccessEmailNotificationMessageBuilder(
            "job_name", job_log_url_template
        )._get_subject("failure", "deploy")
        expected_subject = "[failure][data job deploy] job_name"

        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)

    @patch("time.time", return_value=100000)
    def test_get_job_log_chunk_with_op_id(self, mock_time):
        op_id = "my_op_id"
        actual_chunk = notification_base.SuccessEmailNotificationMessageBuilder(
            "job_name", job_log_url_template
        )._get_job_log_chunk(op_id)
        expected_chunk = '<p>You can find full logs of the job execution <a href="{}"> here <a>.</p>'.format(
            notification_base.SuccessEmailNotificationMessageBuilder(
                "job_name", job_log_url_template
            )._get_job_log_url(op_id)
        )
        self._assert_equal_str_without_whitespaces(expected_chunk, actual_chunk)

    def test_get_job_log_chunk_wo_op_id(self):
        actual_chunk = notification_base.SuccessEmailNotificationMessageBuilder(
            "job_name", job_log_url_template
        )._get_job_log_chunk("")
        self._assert_equal_str_without_whitespaces("", actual_chunk)

    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.UserErrorEmailNotificationMessageBuilder._get_job_log_chunk"
    )
    def test_build_user_error(self, mock_get_job_log_chunk):
        mock_get_job_log_chunk.return_value = "some_chunk"
        job_name = "some-name"
        exec_type = "run"
        msg = "some_message"
        op_id = "my_op_id"
        expected_subject = "[user error][data job run] some-name"
        expected_body = """<p>Dear Versatile Data Kit user,<br />
    Last run of your data job <strong>some-name</strong> has failed.</p>
    <p>Details:</p>
    <p style="padding-left: 30px; color:red;">some_message</p>
    <p>some_chunk</p>
    <p>For more information please visit the user wiki.</p>
    <p>The sender mailbox is not monitored, please do not reply to this email.</p>
    <p>Best,<br />Versatile Data Kit team</p>"""

        (
            actual_subject,
            actual_body,
        ) = notification_base.UserErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(
            exec_type, msg, op_id
        )

        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)
        self._assert_equal_str_without_whitespaces(expected_body, actual_body)

    def test_build_infra_deploy_error(self):
        job_name = "some-name"
        exec_type = "deploy"
        expected_subject = "[platform error][data job deploy] some-name"
        expected_body = (
            """<p>Dear Versatile Data Kit user,<br />
    Last deploy of your data job <strong>some-name</strong> has failed.</p>
    <p>Details:</p>
      <p style="padding-left: 30px; color:red;">There has been a platform error. The error will be resolved by"""
            + " the Versatile Data Kit team. Here are the details:<br />  WHAT HAPPENED : Last deploy of your data job has "
            + "failed<br />WHY IT HAPPENED : There has been a platform error.<br />   CONSEQUENCES : Your new/updated job"
            + " was not deployed. Your job will run its latest successfully deployed version (if any) as scheduled.<br />"
            + "COUNTERMEASURES : The Versatile Data Kit team is working on the issue and will redeploy your job.</p>"
            + "\n   <p>The sender mailbox is not monitored, please do not reply to this email.</p>"
            + "\n   <p>Best,<br />Versatile Data Kit team</p>"
        )

        (
            actual_subject,
            actual_body,
        ) = notification_base.InfraErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(
            exec_type
        )

        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)
        self._assert_equal_str_without_whitespaces(expected_body, actual_body)

    def test_build_infra_run_error(self):
        job_name = "some-name"
        exec_type = "run"
        expected_subject = "[platform error][data job run] some-name"
        expected_body = (
            """<p>Dear Versatile Data Kit user,<br />
    Last run of your data job <strong>some-name</strong> has failed.</p>
    <p>Details:</p>
      <p style="padding-left: 30px; color:red;">There has been a platform error. The error will be resolved by the """
            + "Versatile Data Kit team. Here are the details:<br />  WHAT HAPPENED : Last run of your data job has failed"
            + "<br />WHY IT HAPPENED : There has been a platform error.<br />   CONSEQUENCES : Job will be restarted automatically on failure up to 3 times."
            + "<br />COUNTERMEASURES : No customer action is required. If the 3 restarts fail, Versatile Data Kit team will investigate the "
            + "error and ensure job will continue to run as expected. If you want to receive notification on "
            + "successful job execution, you can set it up in config.ini</p>"
            + "\n   <p>The sender mailbox is not monitored, please do not reply to this email.</p>"
            + "\n   <p>Best,<br />Versatile Data Kit team</p>"
        )
        (
            actual_subject,
            actual_body,
        ) = notification_base.InfraErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(
            exec_type
        )
        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)
        self._assert_equal_str_without_whitespaces(expected_body, actual_body)

    @patch("logging.getLogger")
    def test_build_infra_unknown_exec_type_error(self, mock_logger):
        job_name = "some-name"
        exec_type = "unknown"
        expected_subject = "[platform error][data job ] some-name"
        expected_body = """<p>Dear Versatile Data Kit user,<br />
    Last  of your data job <strong>some-name</strong> has failed.</p>
    <p>Details:</p>
      <p style="padding-left: 30px; color:red;">There has been a platform error. The error will be resolved by the Versatile Data Kit team.</p>
    <p>The sender mailbox is not monitored, please do not reply to this email.</p>
    <p>Best,<br />Versatile Data Kit team</p>"""

        (
            actual_subject,
            actual_body,
        ) = notification_base.InfraErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(
            exec_type
        )

        mock_logger.return_value.warning.assert_called_once_with(
            f"Unknown exec_type [{exec_type}]"
        )
        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)
        self._assert_equal_str_without_whitespaces(expected_body, actual_body)

    @patch(
        "vdk.internal.builtin_plugins.notification.notification_base.SuccessEmailNotificationMessageBuilder._get_job_log_chunk"
    )
    def test_build_success(self, mock_get_job_log_chunk):
        mock_get_job_log_chunk.return_value = "some_chunk"
        op_id = "my_op_id"
        job_name = "some-name"
        exec_type = "run"
        expected_subject = "[success][data job run] some-name"
        expected_body = """<p>Dear Versatile Data Kit user,<br />
    Last run of your data job <strong>some-name</strong> has succeeded.</p>
    some_chunk
    <p>The sender mailbox is not monitored, please do not reply to this email.</p>
    <p>Best,<br />Versatile Data Kit team</p>"""

        (
            actual_subject,
            actual_body,
        ) = notification_base.SuccessEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(
            exec_type, op_id=op_id
        )

        print("SUBJECT", actual_subject)
        print("BODY:", actual_body)

        self._assert_equal_str_without_whitespaces(expected_subject, actual_subject)
        self._assert_equal_str_without_whitespaces(expected_body, actual_body)

    def _assert_equal_str_without_whitespaces(self, expected, actual):
        return self.assertEqual(expected.replace(" ", ""), actual.replace(" ", ""))
