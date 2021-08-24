# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from taurus.vdk.builtin_plugins.config.job_config import JobConfigKeys
from taurus.vdk.core.config import Configuration
from taurus.vdk.core.config import ConfigurationBuilder

NOTIFICATION_JOB_LOG_URL_PATTERN = "NOTIFICATION_JOB_LOG_URL_PATTERN"
NOTIFICATION_EMAIL_CC_LIST = "NOTIFICATION_EMAIL_CC_LIST"
NOTIFICATION_SENDER = "NOTIFICATION_SENDER"
NOTIFICATION_SMTP_HOST = "NOTIFICATION_SMTP_HOST"


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

    def get_smtp_host(self) -> str:
        return str(self.__config[NOTIFICATION_SMTP_HOST])


def __add_job_notified_configuration_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=JobConfigKeys.TEAM,
        default_value="",
        description="Specified which is the team that owns the data job. "
        "Value is case-sensitive and must be an actual team name as specified during job creation."
        "",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution "
        "failure caused by user code or user configuration problem. "
        " For example: if the job contains an SQL script with syntax error.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution failure "
        "caused by a platform problem, including job execution delays.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified on job execution success.",
    )
    config_builder.add(
        key=JobConfigKeys.NOTIFIED_ON_JOB_DEPLOY,
        default_value="",
        description="Semicolon-separated list of email addresses to be notified of job deployment outcome",
    )
    config_builder.add(
        key=JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS,
        default_value=False,
        description="Flag to enable or disable the email notifications sent to the recipients listed above "
        "for each data job run attempt.",
    )


def add_definitions(config_builder: ConfigurationBuilder):
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
    config_builder.add(
        key=NOTIFICATION_SMTP_HOST,
        default_value="smtp.vmware.com",
        description="The SMTP host used for to send the notification email.",
    )
    __add_job_notified_configuration_definitions(config_builder)
