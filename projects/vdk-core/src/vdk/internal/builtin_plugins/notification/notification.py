# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.config.vdk_config import LOG_CONFIG
from vdk.internal.builtin_plugins.notification import notification_base
from vdk.internal.builtin_plugins.notification import notification_configuration
from vdk.internal.builtin_plugins.notification.notification_configuration import (
    NotificationConfiguration,
)
from vdk.internal.builtin_plugins.notification.notification_configuration import (
    SmtpConfiguration,
)
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys

log = logging.getLogger(__name__)


def __get_list(value: str) -> List[str]:
    result = value.split(";") if value else []
    result = [v.strip() for v in result if len(v.strip()) > 0]
    return result


def _notify(error_overall, user_error, configuration, state):
    notification_cfg = NotificationConfiguration(configuration)

    if (
        configuration.get_value(LOG_CONFIG).lower() == "local"
        and notification_cfg.get_notification_enabled() is False
    ):
        return
    log.debug(
        f"Prepare to send notification if necessary: error_overall: {error_overall}"
    )

    job_name = state.get(ExecutionStateStoreKeys.JOB_NAME)
    op_id = state.get(CommonStoreKeys.OP_ID)

    job_log_url_template = notification_cfg.get_job_log_url_pattern()
    cc = notification_cfg.get_email_cc_list()
    sender = notification_cfg.get_sender()
    smtp_cfg = SmtpConfiguration(configuration)

    if not error_overall:
        recipients = __get_list(
            configuration.get_value(JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS.value)
        )
        if recipients:
            subject, body = notification_base.SuccessEmailNotificationMessageBuilder(
                job_name, job_log_url_template
            ).build(exec_type="run", op_id=op_id)
            notification_base.EmailNotification(
                recipients=recipients, cc=cc, smtp_cfg=smtp_cfg, sender=sender
            ).notify(subject, body)
        else:
            log.debug(
                "No recipients configured to send on successful run. No notification is sent"
            )
        return

    if user_error:
        recipients = __get_list(
            configuration.get_value(
                JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR.value
            )
        )
        if recipients:
            subject, body = notification_base.UserErrorEmailNotificationMessageBuilder(
                job_name, job_log_url_template
            ).build(exec_type="run", op_id=op_id, msg=user_error)
            notification_base.EmailNotification(
                recipients=recipients, cc=cc, smtp_cfg=smtp_cfg, sender=sender
            ).notify(subject, body)
        else:
            log.debug(
                "No recipients configured to send on user error. No notification is sent"
            )
        return

    recipients = __get_list(
        configuration.get_value(
            JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR.value
        )
    )

    if recipients:
        subject, body = notification_base.InfraErrorEmailNotificationMessageBuilder(
            job_name, job_log_url_template
        ).build(exec_type="run", op_id=op_id)
        notification_base.EmailNotification(
            recipients=recipients, cc=cc, smtp_cfg=smtp_cfg, sender=sender
        ).notify(subject, body)
    else:
        log.debug(
            "No recipients configured to send on platform error. No notification is sent"
        )

    log.debug("Notification for Data Job state has been sent to listed recipients")


class NotificationPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        notification_configuration.add_definitions(config_builder)

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int):
        if context.configuration.get_value(
            JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value
        ):
            _notify(
                errors.get_blamee_overall(),  # TODO: get this from context
                errors.get_blamee_overall_user_error(),  # TODO: get this from context
                context.configuration,
                context.state,
            )
