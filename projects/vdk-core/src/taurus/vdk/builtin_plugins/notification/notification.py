# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config.job_config import JobConfigKeys
from taurus.vdk.builtin_plugins.config.vdk_config import LOG_CONFIG
from taurus.vdk.builtin_plugins.notification import notification_base
from taurus.vdk.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from taurus.vdk.core import errors
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import CommonStoreKeys

log = logging.getLogger(__name__)

NOTIFICATION_JOB_LOG_URL_PATTERN = "NOTIFICATION_JOB_LOG_URL_PATTERN"
NOTIFICATION_EMAIL_CC_LIST = "NOTIFICATION_EMAIL_CC_LIST"
NOTIFICATION_SMTP_HOST = "NOTIFICATION_SMTP_HOST"
NOTIFICATION_SENDER = "NOTIFICATION_SENDER"


def _notify(error_overall, user_error, configuration, state):
    if configuration.get_value(LOG_CONFIG).lower() == "local":
        return

    job_name = state.get(ExecutionStateStoreKeys.JOB_NAME)
    op_id = state.get(CommonStoreKeys.OP_ID)

    job_log_url_template = configuration.get_value(NOTIFICATION_JOB_LOG_URL_PATTERN)
    cc = configuration.get_value(NOTIFICATION_EMAIL_CC_LIST)
    smtp_host = configuration.get_value(NOTIFICATION_SMTP_HOST)
    sender = configuration.get_value(NOTIFICATION_SENDER)

    if not error_overall:
        recipients = configuration.get_value(JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS)
        if recipients:
            subject, body = notification_base.SuccessEmailNotificationMessageBuilder(
                job_name, job_log_url_template
            ).build(exec_type="run", op_id=op_id)
            notification_base.EmailNotification(
                recipients=recipients, cc=cc, smtp_host=smtp_host, sender=sender
            ).notify(subject, body)
        return

    if user_error:
        recipients = configuration.get_value(
            JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR
        )
        if recipients:
            subject, body = notification_base.UserErrorEmailNotificationMessageBuilder(
                job_name, job_log_url_template
            ).build(exec_type="run", op_id=op_id, msg=user_error)
            notification_base.EmailNotification(
                recipients=recipients, cc=cc, smtp_host=smtp_host, sender=sender
            ).notify(subject, body)
        return

    recipients = configuration.get_value(
        JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR
    )

    if recipients:
        subject, body = notification_base.InfraErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(exec_type="run", op_id=op_id)
        notification_base.EmailNotification(
            recipients=recipients, cc=cc, smtp_host=smtp_host, sender=sender
        ).notify(subject, body)

    log.debug("Notification for Data Job state has been sent to listed recipients")


class NotificationPlugin:
    @hookimpl
    def vdk_configure(self, config_builder: ConfigurationBuilder):
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
            description="A comma separated string of email addresses to be CC'd in the notification email.",
        )
        config_builder.add(
            key=NOTIFICATION_SMTP_HOST,
            default_value="smtp.vmware.com",
            description="The SMTP host used for to send the notification email.",
        )
        config_builder.add(
            key=NOTIFICATION_SENDER,
            default_value="data-pipelines@vmware.com",
            description="The email address, from which notification emails are sent.",
        )

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int):
        if context.configuration.get_value(JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS):
            _notify(
                errors.get_blamee_overall(),  # TODO: get this from context
                errors.get_blamee_overall_user_error(),  # TODO: get this from context
                context.configuration,
                context.state,
            )
