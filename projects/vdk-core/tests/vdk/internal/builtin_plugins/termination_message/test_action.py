# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.internal.builtin_plugins.termination_message.action import WriteToFileAction


class TerminationActionTest(unittest.TestCase):
    @patch("builtins.open")
    def test_write_to_file_action_with_empty_file(self, mock_open):
        action = WriteToFileAction("")
        action.success()
        mock_open.assert_not_called()

    @patch("builtins.open")
    def test_write_to_file_action_with_success(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        action = WriteToFileAction("somefile")
        action.success()
        # Assert that the write() method of the file returned by the open() mocked method is called once
        mock_file.__enter__.return_value.write.assert_called_once_with("Success\n")

    @patch("builtins.open")
    def test_write_to_file_action_with_user_error(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        action = WriteToFileAction("somefile")
        action.user_error()
        # Assert that the write() method of the file returned by the open() mocked method is called once
        mock_file.__enter__.return_value.write.assert_called_once_with("User error\n")

    @patch("builtins.open")
    def test_write_to_file_action_with_platform_error(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        action = WriteToFileAction("somefile")
        action.platform_error()
        # Assert that the write() method of the file returned by the open() mocked method is called once
        mock_file.__enter__.return_value.write.assert_called_once_with(
            "Platform error\n"
        )

    @patch("builtins.open")
    @patch("logging.Logger.debug")
    def test_write_to_file_when_error_happens(self, mock_logger_debug, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__.return_value.write.side_effect = OSError()
        mock_open.return_value = mock_file
        action = WriteToFileAction("somefile")
        action.platform_error()
        # Assert that the mocked logger method is called once
        mock_logger_debug.expect_to_be_called_once()
