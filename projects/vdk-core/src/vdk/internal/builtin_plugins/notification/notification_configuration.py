# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

NOTIFICATION_ENABLED = "NOTIFICATION_ENABLED"
NOTIFICATION_JOB_LOG_URL_PATTERN = "NOTIFICATION_JOB_LOG_URL_PATTERN"
NOTIFICATION_EMAIL_CC_LIST = "NOTIFICATION_EMAIL_CC_LIST"
NOTIFICATION_SENDER = "NOTIFICATION_SENDER"
NOTIFICATION_SMTP_HOST = "NOTIFICATION_SMTP_HOST"
NOTIFICATION_SMTP_PORT = "NOTIFICATION_SMTP_PORT"
NOTIFICATION_SMTP_USE_TLS = "NOTIFICATION_SMTP_USE_TLS"
NOTIFICATION_SMTP_LOGIN_USERNAME = "NOTIFICATION_SMTP_LOGIN_USERNAME"
NOTIFICATION_SMTP_LOGIN_PASSWORD = "NOTIFICATION_SMTP_LOGIN_PASSWORD"
NOTIFICATION_SMTP_DEBUG_LEVEL = "NOTIFICATION_SMTP_DEBUG_LEVEL"


class NotificationConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_job_log_url_pattern(self) -> str:
        return str(self.__config[NOTIFICATION_JOB_LOG_URL_PATTERN])

    def get_email_cc_list(self) -> List[str]:
        # TODO: we should considure ConfigurationBuilder to support List type for configuration values
        # and automatically parses them as below
        cc_list = str(self.__config[NOTIFICATION_EMAIL_CC_LIST])
        cc_result = cc_list.split(";") if cc_list else []
        cc_result = [cc.strip() for cc in cc_result if len(cc.strip()) > 0]
        return cc_result

    def get_sender(self) -> str:
        return str(self.__config[NOTIFICATION_SENDER])

    def get_notification_enabled(self):
        return bool(self.__config[NOTIFICATION_ENABLED])


class SmtpConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_host(self) -> str:
        return str(self.__config[NOTIFICATION_SMTP_HOST])

    def get_port(self) -> int:
        return int(self.__config[NOTIFICATION_SMTP_PORT])

    def get_use_tls(self) -> bool:
        return bool(self.__config[NOTIFICATION_SMTP_USE_TLS])

    def get_login_username(self) -> str:
        return str(self.__config[NOTIFICATION_SMTP_LOGIN_USERNAME])

    def get_login_password(self) -> str:
        return str(self.__config[NOTIFICATION_SMTP_LOGIN_PASSWORD])

    def get_debug_level(self) -> int:
        return int(self.__config[NOTIFICATION_SMTP_DEBUG_LEVEL])


def __add_job_notified_configuration_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution "
        "failure caused by user code or user configuration problem. "
        "For example: if the job contains an SQL script with syntax error.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution failure "
        "caused by a platform problem, including job execution delays.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution success.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_DEPLOY.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified of job deployment outcome",
    )
    config_builder.add(
        key=JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value,
        default_value=False,
        description="Flag to enable or disable the email notifications sent to the recipients listed above "
        "for each data job run attempt.",
    )


def __add_smtp_configuration_definitions(config_builder):
    config_builder.add(
        key=NOTIFICATION_SMTP_HOST,
        default_value="smtp.vmware.com",
        description="The SMTP host used for sending the notification email.",
    )
    config_builder.add(
        key=NOTIFICATION_SMTP_PORT,
        default_value=25,
        description="The SMTP port used for to send the notification email.",
    )
    config_builder.add(
        key=NOTIFICATION_SMTP_USE_TLS,
        default_value=False,
        description="Set to true if you want to use secure connection over TLS/SSL.",
    )
    config_builder.add(
        key=NOTIFICATION_SMTP_LOGIN_USERNAME,
        default_value="",
        description="Login username to use when connecting to SMTP server. If empty no login is attempted.",
    )
    config_builder.add(
        key=NOTIFICATION_SMTP_LOGIN_PASSWORD,
        default_value="",
        description="Login password to use when connecting to SMTP server.",
    )
    config_builder.add(
        key=NOTIFICATION_SMTP_DEBUG_LEVEL,
        default_value=1,
        description="SMTP debug level. A non-zero value results in debug messages for connection "
        "and for all messages sent to and received from the SMTP server.",
    )


def __add_job_notified_configuration_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution "
        "failure caused by user code or user configuration problem. "
        "For example: if the job contains an SQL script with syntax error.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution failure."
        "caused by a platform problem, including job execution delays.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution success.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_DEPLOY.value,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified of job deployment outcome.",
    )
    config_builder.add(
        key=JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value,
        default_value=False,
        description="Flag to enable or disable the email notifications sent to the recipients listed above "
        "for each data job run attempt.",
    )


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=NOTIFICATION_ENABLED,
        default_value=False,
        description="Set to true if you want to enable notifications regardless if it is run locally or not.",
    )
    config_builder.add(
        key=NOTIFICATION_JOB_LOG_URL_PATTERN,
        default_value=(
            "https://example-job-log-url.com/{op_id},{start_time_ms},{end_time_ms}"
        ),
        description=(
            "The URL template used to find the full log of a particular job. "
            "It is further parametrized with the job's op_id and start and end times "
            "by replacing the bracketed parts of the url with the respective values. "
            "(For example, '{op_id}' becomes the actual op_id of the job.)"
        ),
    )
    config_builder.add(
        key=NOTIFICATION_EMAIL_CC_LIST,
        default_value="",
        description="A semicolon-separated separated string of email addresses to be CC'd in the notification email.",
    )
    config_builder.add(
        key=NOTIFICATION_SENDER,
        default_value="data-pipelines@vmware.com",
        description="The email address, from which notification emails are sent.",
    )

    __add_smtp_configuration_definitions(config_builder)
    __add_job_notified_configuration_definitions(config_builder)
