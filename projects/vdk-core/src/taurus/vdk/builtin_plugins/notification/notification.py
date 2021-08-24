# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config.job_config import JobConfigKeys
from taurus.vdk.builtin_plugins.config.vdk_config import LOG_CONFIG
from taurus.vdk.builtin_plugins.notification import notification_base
from taurus.vdk.builtin_plugins.notification import notification_configuration
from taurus.vdk.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from taurus.vdk.core import errors
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.core.context import CoreContext
from taurus.vdk.core.statestore import CommonStoreKeys

log = logging.getLogger(__name__)


def _notify(error_overall, user_error, configuration, state):
    if configuration.get_value(LOG_CONFIG).lower() == "local":
        return

    job_name = state.get(ExecutionStateStoreKeys.JOB_NAME)
    op_id = state.get(CommonStoreKeys.OP_ID)

    notification_cfg = notification_configuration.NotificationConfiguration(
        configuration
    )

    job_log_url_template = notification_cfg.get_job_log_url_pattern()
    cc = notification_cfg.get_email_cc_list()
    smtp_host = notification_cfg.get_smtp_host()
    sender = notification_cfg.get_sender()

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
        notification_configuration.add_definitions(config_builder)

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int):
        if context.configuration.get_value(JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS):
            _notify(
                errors.get_blamee_overall(),  # TODO: get this from context
                errors.get_blamee_overall_user_error(),  # TODO: get this from context
                context.configuration,
                context.state,
            )
