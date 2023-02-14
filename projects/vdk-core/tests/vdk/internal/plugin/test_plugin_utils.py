# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest import mock

import click
from vdk.api.plugin.plugin_utils import set_defaults_for_all_commands
from vdk.api.plugin.plugin_utils import set_defaults_for_specific_command
from vdk.internal.core.errors import VdkConfigurationError


class TestPluginUtils(unittest.TestCase):
    def test_set_defaults_for_specific_command_dict_is_empty(self):
        mock_root_command = mock.MagicMock(click.Group)

        set_defaults_for_specific_command(mock_root_command, "test-command", {})

    def test_set_defaults_for_all_commands_dict_is_empty(self):
        mock_root_command = mock.MagicMock(click.Group)

        set_defaults_for_all_commands(mock_root_command, {})

    def test_set_defaults_for_specific_command_command_doesnt_exist(self):
        mock_root_command = mock.MagicMock(click.Group)
        mock_root_command.get_command.return_value = None

        with self.assertRaises(VdkConfigurationError):
            set_defaults_for_specific_command(
                mock_root_command, "test-command", {"a": "1", "b": "2"}
            )

    def test_set_defaults_for_specific_command_root_command_is_wrong_type(self):
        with self.assertRaises(VdkConfigurationError):
            set_defaults_for_specific_command(
                "test-root-command", "test-command", {"a": "1", "b": "2"}
            )

    def test_set_defaults_for_all_commands_root_command_is_wrong_type(self):
        with self.assertRaises(VdkConfigurationError):
            set_defaults_for_all_commands("test-root-command", {"a": "1", "b": "2"})
