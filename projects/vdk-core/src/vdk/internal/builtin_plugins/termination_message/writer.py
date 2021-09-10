# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.vdk_config import LOG_CONFIG
from vdk.internal.builtin_plugins.termination_message import action
from vdk.internal.builtin_plugins.termination_message import (
    writer_configuration,
)
from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    WriterConfiguration,
)
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext

log = logging.getLogger(__name__)


class TerminationMessageWriterPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        writer_configuration.add_definitions(config_builder)

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int):
        self._write_termination_message(
            errors.get_blamee_overall(),  # TODO: get this from context
            errors.get_blamee_overall_user_error(),  # TODO: get this from context
            context.configuration,
        )

    def _write_termination_message(self, error_overall, user_error, configuration):
        termination_message_writer_cfg = WriterConfiguration(configuration)

        try:
            termination_message_output_file = (
                termination_message_writer_cfg.get_output_file()
            )

            if (
                termination_message_writer_cfg.get_writer_enabled()
                and termination_message_output_file
            ):
                # Hide termination messages when running locally
                show_termination_log_messages = (
                    configuration.get_value(LOG_CONFIG).lower() != "local"
                )
                termination_action = action.WriteToFileAction(
                    termination_message_output_file, show_termination_log_messages
                )

                if show_termination_log_messages:
                    log.debug(
                        f'Writing termination message to file "{termination_message_output_file}"'
                    )
                self._execute_termination_action(
                    termination_action, error_overall, user_error
                )
        except:
            log.exception("Failed to write termination message.")

    @staticmethod
    def _execute_termination_action(
        action, error_overall, user_error, execution_skipped=False
    ):
        if execution_skipped:
            action.skipped()
        elif not error_overall:
            action.success()
        elif user_error:
            action.user_error()
        else:
            action.platform_error()
