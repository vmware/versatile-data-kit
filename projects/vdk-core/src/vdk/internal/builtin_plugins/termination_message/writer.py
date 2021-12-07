# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.vdk_config import LOG_CONFIG
from vdk.internal.builtin_plugins.termination_message import (
    writer_configuration,
)
from vdk.internal.builtin_plugins.termination_message.file_util import (
    WriteToFileAction,
)
from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    WriterConfiguration,
)
from vdk.internal.builtin_plugins.version.version import get_version
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
        self.write_termination_message(
            errors.get_blamee_overall(),  # TODO: get this from context
            errors.get_blamee_overall_user_error(),  # TODO: get this from context
            context.configuration,
        )

    def write_termination_message(
        self, error_overall, user_error, configuration, execution_skipped=False
    ):
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
                file_util = WriteToFileAction(
                    termination_message_output_file, show_termination_log_messages
                )

                if show_termination_log_messages:
                    log.debug(
                        f'Writing termination message to file "{termination_message_output_file}"'
                    )
                self._execute_termination_action(
                    file_util, error_overall, user_error, execution_skipped
                )
        except Exception as e:
            log.exception(f"Failed to write termination message. See exception: {e}")

    @staticmethod
    def _execute_termination_action(
        file_util, error_overall, user_error, execution_skipped
    ):

        termination_message = {"vdk_version": get_version()}

        if execution_skipped:
            status = "Skipped"
        elif not error_overall:
            status = "Success"
        elif user_error:
            status = "User error"
        else:
            status = "Platform error"

        termination_message["status"] = status
        file_util.append_to_file(json.dumps(termination_message))
