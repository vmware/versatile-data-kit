# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.termination_message.writer import (
    TerminationMessageWriterPlugin,
)
from vdk.internal.builtin_plugins.version.version import get_version
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import get_blamee_overall
from vdk.internal.core.statestore import StateStore


class TestTerminationMessageWriterPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.termination_plugin = TerminationMessageWriterPlugin()
        configuration_builder = ConfigurationBuilder()
        self.termination_plugin.vdk_configure(configuration_builder)

        self.configuration = (
            configuration_builder.add(
                key="TERMINATION_MESSAGE_WRITER_OUTPUT_FILE",
                default_value="filename.txt",
            )
            .add(
                key=vdk_config.LOG_CONFIG,
                default_value="local",
            )
            .build()
        )

    def tearDown(self) -> None:
        os.remove(
            self.configuration.get_value("TERMINATION_MESSAGE_WRITER_OUTPUT_FILE")
        )

    def test_double_write(self):
        # write a success message
        self.termination_plugin.write_termination_message(
            False, False, self.configuration, False
        )
        # check message was written successfully
        self._check_message_status("Success")
        # write another message
        self.termination_plugin.write_termination_message(
            False, False, self.configuration, False
        )
        # check idempotence
        self._check_message_status("Success")

    def test_last_message_persisted(self):
        # write a success message
        self.termination_plugin.write_termination_message(
            False, False, self.configuration, False
        )
        # check message was written successfully
        self._check_message_status("Success")
        # write failure message
        self.termination_plugin.write_termination_message(
            True, False, self.configuration, False
        )
        # check fail message is present
        self._check_message_status("Platform error")

    def test_user_error_message(self):
        # write user error message
        self.termination_plugin.write_termination_message(
            True, True, self.configuration, False
        )
        # check message was written successfully
        self._check_message_status("User error")
        # write user error message
        self.termination_plugin.write_termination_message(
            True, True, self.configuration, False
        )
        # check message idempotent
        self._check_message_status("User error")

    def test_execution_skipped_message(self):
        # write execution skipped
        self.termination_plugin.write_termination_message(
            False, False, self.configuration, True
        )
        # check message was written successfully
        self._check_message_status("Skipped")
        # check idempotence
        self.termination_plugin.write_termination_message(
            False, False, self.configuration, True
        )
        # check message was written successfully
        self._check_message_status("Skipped")

    def _check_message_status(self, expected_status):
        expected_status = (
            f'{{"vdk_version": "{get_version()}", "status": "{expected_status}"}}'
        )
        with open(
            self.configuration.get_value("TERMINATION_MESSAGE_WRITER_OUTPUT_FILE")
        ) as file:
            assert file.read() == expected_status


class WriterTest(unittest.TestCase):
    @patch("builtins.open")
    @patch(f"{get_blamee_overall.__module__}.{get_blamee_overall.__name__}")
    def test_writer(self, get_blamee_overall, mock_open):
        get_blamee_overall.return_value = None
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        vdk = TerminationMessageWriterPlugin()

        configuration_builder = ConfigurationBuilder()
        vdk.vdk_configure(configuration_builder)

        configuration = (
            configuration_builder.add(
                key="TERMINATION_MESSAGE_WRITER_OUTPUT_FILE",
                default_value="filename.txt",
            )
            .add(
                key=vdk_config.LOG_CONFIG,
                default_value="local",
            )
            .build()
        )

        context = CoreContext(
            MagicMock(spec=IPluginRegistry),
            configuration,
            MagicMock(spec=StateStore),
        )

        vdk.vdk_exit(context, 0)

        # Assert that the write() method of the file returned by the open() mocked method is called once
        mock_file.__enter__.return_value.write.assert_called_once_with(
            '{"vdk_version": "%s", "status": "Success"}' % get_version()
        )
