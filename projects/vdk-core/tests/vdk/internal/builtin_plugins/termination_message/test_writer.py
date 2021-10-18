# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
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
