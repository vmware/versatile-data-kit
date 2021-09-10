# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import smtplib
import time
from abc import ABC
from abc import abstractmethod
from email.mime.text import MIMEText
from functools import reduce
from typing import List

from vdk.internal.builtin_plugins.notification.notification_configuration import (
    SmtpConfiguration,
)
from vdk.internal.core import errors

log = logging.getLogger(__name__)


class LoggingSMTP(smtplib.SMTP):
    """
    Subclass to replace the print statements with logging statements so that debug output can be captured
    """

    def _print_debug(self, *args):
        message = reduce((lambda msg1, msg2: str(msg1) + str(msg2)), iter(args))
        log.debug(message)


class INotification(ABC):
    @abstractmethod
    def notify(self, title, body):
        """
        Sends a message to recipients using a predefined channel.
        Both the receivers and the channel are specified in config.ini.
        :param title: message title
        :param body: message content
        """
        pass


class EmailNotification(INotification):
    def __init__(
        self,
        recipients: List[str],
        cc: List[str],
        smtp_cfg: SmtpConfiguration,
        sender: str,
    ):
        """
        :param recipients: list of emails
        :param sender: sender email
        :param cc: list of emails
        """
        log.debug(
            f"New EmailNotification prepared: sender: {sender}; cc: {cc}; recipeints: {recipients}"
        )
        self._sender = sender
        self._cc = [] if cc is None else cc
        self._smtp_cfg = smtp_cfg
        self._recipients = recipients

    def notify(self, subject, body):
        """
        Sends an email to the specified recipients. If there are no valid recipient addresses, it sends the email
        to the CC'd addresses, assuming at least one of them is valid. If none of them are, an appropriate error is
        logged, and no email is sent.

        :param subject: The subject of the email
        :param body: The email job
        """
        valid_recipients = ",".join(self._get_valid_recipients())
        if valid_recipients:
            email_message = self._build_message(subject, body, valid_recipients)
            self._send_message(email_message)
        else:
            valid_cc = ",".join(self._get_valid_cc())
            if valid_cc:
                logging.getLogger(__name__).warning(
                    "No valid recipient address is given"
                )
                email_message = self._build_message(
                    subject,
                    (
                        "This message is sent to the list of CC'd addresses "
                        "because none of the listed recipient addresses are valid, or none were provided.\n\n"
                    )
                    + body,
                    valid_cc,
                )
                self._send_message(email_message)
            elif (not valid_cc) and self._cc:
                logging.getLogger(__name__).warning(
                    "No valid recipients or CC addresses given"
                )
            else:
                logging.getLogger(__name__).debug("Empty list of recipients is given")

    def _send_message(self, msg):
        log.debug(f"Send message {msg}")
        s = self.__smtp_server()
        s.send_message(msg)
        s.quit()

    def _build_message(self, subject, body, recipients):
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = self._sender
        msg["To"] = recipients
        msg["Cc"] = ",".join(self._get_valid_cc())
        return msg

    def _email_address_exists(self, email_address):
        """
        Checks if a particular email address is valid or not. The reason for this is that if an attempt to send
        an email to a non-valid address is made, that attempt will fail and no email will be sent to any of the
        specified addresses, regardless is any of the rest were valid or not.


        :param email_address: The email address in string form
        :return: a boolean specifying if the address is valid or not
        """
        s = self.__smtp_server()
        try:
            s.helo()
            s.mail("whatever")
            resp = s.rcpt(email_address)
            return resp[0] == 250
        except smtplib.SMTPServerDisconnected as e:
            log.warning(
                "SMTP connection error while checking if email address exists: %s", e
            )
            return True
        finally:
            s.quit()

    def __smtp_server(self):
        s = LoggingSMTP(self._smtp_cfg.get_host(), port=self._smtp_cfg.get_port())
        if self._smtp_cfg.get_use_tls():
            s.starttls()
        if self._smtp_cfg.get_login_username():
            s.login(
                self._smtp_cfg.get_login_username(), self._smtp_cfg.get_login_password()
            )
        s.set_debuglevel(self._smtp_cfg.get_debug_level())
        return s

    def _get_valid_recipients(self):
        return [x.strip() for x in self._recipients if self._email_address_exists(x)]

    def _get_valid_cc(self):
        return [x.strip() for x in self._cc if self._email_address_exists(x)]


class EmailNotificationMessageBuilder(ABC):
    def __init__(self, job_name, job_log_url_template):
        self._job_name = job_name

        self.JOB_LOG_URL_TEMPLATE = job_log_url_template

        self.NOTIFICATION_MSG_TEMPLATE = """<p>Dear Versatile Data Kit user,<br />
   Last {exec_type} of your data job <strong>{job_name}</strong> has {result}.</p>
   {result_msg}
   <p>The sender mailbox is not monitored, please do not reply to this email.</p>
   <p>Best,<br />Versatile Data Kit team</p>"""

        self.USER_ERROR_TEMPLATE = """<p>Details:</p>
   <p style="padding-left: 30px; color:red;">{error_msg}</p>
   <p>{job_log_link}</p>
   <p>For more information please visit the user wiki.</p>"""

        self.INFRA_ERROR_MSG = """<p>Details:</p>
     <p style="padding-left: 30px; color:red;">{error_msg}</p>"""

        self.NOTIFICATION_MSG_SUBJECT_TEMPLATE = (
            "[{result}][data job {exec_type}] {job_name}"
        )

    @abstractmethod
    def build(self, exec_type, msg, op_id):
        """
        Builds a (subject, body) tuple to be used as input for EmailNotification.notify
        :param op_id: execution id of the data job
        :param msg: string to be included into the message template
        :param exec_type: 'run' or 'deploy'
        :return: (subject, body) tuple
        """
        pass

    def _get_job_log_url(self, op_id):
        now = int(round(time.time() * 1000))
        hour = 60 * 60 * 1000
        start_time_ms = now - 24 * hour
        end_time_ms = now + hour
        return self.JOB_LOG_URL_TEMPLATE.format(
            op_id=op_id, start_time_ms=start_time_ms, end_time_ms=end_time_ms
        )

    def _get_job_log_chunk(self, op_id):
        return (
            '<p>You can find full logs of the job execution <a href="{}"> here <a>.</p>'.format(
                self._get_job_log_url(op_id.strip())
            )
            if op_id
            else ""
        )

    def _get_subject(self, result, exec_type):
        return self.NOTIFICATION_MSG_SUBJECT_TEMPLATE.format(
            result=result, exec_type=exec_type, job_name=self._job_name
        )


class UserErrorEmailNotificationMessageBuilder(EmailNotificationMessageBuilder):
    def build(self, exec_type, msg="", op_id=""):
        user_error = self.USER_ERROR_TEMPLATE.format(
            error_msg=msg, job_log_link=self._get_job_log_chunk(op_id)
        )
        subject = self._get_subject("user error", exec_type)
        html_body = self.NOTIFICATION_MSG_TEMPLATE.format(
            exec_type=exec_type,
            job_name=self._job_name,
            result="failed",
            result_msg=user_error,
        )
        return subject, html_body


class InfraErrorEmailNotificationMessageBuilder(EmailNotificationMessageBuilder):
    def build(self, exec_type, msg="", op_id=""):
        if exec_type == "deploy":
            error_msg = errors.ErrorMessage(
                "There has been a platform error. The error will be resolved by the Versatile Data Kit team. "
                "Here are the details:",
                "Last deploy of your data job has failed",
                "There has been a platform error.",
                "Your new/updated job was not deployed. Your job will run its latest "
                "successfully deployed version (if any) as scheduled.",
                "The Versatile Data Kit team is working on the issue and will redeploy your job.",
            ).to_html()
        elif exec_type == "run":
            error_msg = errors.ErrorMessage(
                "There has been a platform error. The error will be resolved by the Versatile Data Kit team. "
                "Here are the details:",
                "Last run of your data job has failed",
                "There has been a platform error.",
                "Job will be restarted automatically on failure up to 3 times.",
                "No customer action is required. If the 3 restarts fail, Versatile Data Kit team will investigate the "
                "error and ensure job will continue to run as expected. If you want to receive notification on "
                "successful job execution, you can set it up in config.ini",
            ).to_html()
        else:
            logging.getLogger(__name__).warning(
                "Unknown exec_type [{}]".format(
                    exec_type if exec_type is not None else "None"
                )
            )
            exec_type = ""
            error_msg = "There has been a platform error. The error will be resolved by the Versatile Data Kit team."

        subject = self._get_subject("platform error", exec_type)
        html_body = self.NOTIFICATION_MSG_TEMPLATE.format(
            exec_type=exec_type,
            job_name=self._job_name,
            result="failed",
            result_msg=self.INFRA_ERROR_MSG.format(error_msg=error_msg),
        )
        return subject, html_body


class SuccessEmailNotificationMessageBuilder(EmailNotificationMessageBuilder):
    def build(self, exec_type, msg="", op_id=""):
        additional_info = self._get_job_log_chunk(op_id)
        subject = self._get_subject("success", exec_type)
        html_body = self.NOTIFICATION_MSG_TEMPLATE.format(
            exec_type=exec_type,
            job_name=self._job_name,
            result="succeeded",
            result_msg=additional_info,
        )
        return subject, html_body
