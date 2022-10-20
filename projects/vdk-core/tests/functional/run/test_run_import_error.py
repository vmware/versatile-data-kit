# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.internal.cli_entry import main


class TestImportErrors(unittest.TestCase):
    @patch(
        "pluggy._manager.PluginManager.load_setuptools_entrypoints",
        side_effect=ImportError("Test import error."),
    )
    @patch("os._exit", side_effect=Exception("VDK run termination exception."))
    @patch(
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFileAction.write_to_file"
    )
    def test_run(
        self,
        file_util: MagicMock,
        patched_exit: MagicMock,
        load_setuptools_entrypoints: MagicMock,
    ):
        """
        This test simulates a scenario where a user imports a library that
        has a clash with vdk internal imports. We want to check that the
        exception is handled by vdk logic and exit status is not 0.
        :param file_util: the patched method that writes the termination message
        :param patched_exit: call to os._exit, we want to patch it here since we
                             don't want to exit the test suite. Also throws exception
                             as side effect to simulate the actual system exit call.
        :param load_setuptools_entrypoints:
        :return:
        """
        with self.assertRaises(Exception):
            main()

        # WriteToFileAction.write_to_file() method which takes
        # the termination message as parameter. We check that
        # ImportError resulted in user error termination message.
        file_util.assert_called_once()
        assert '"status": "User error"' in str(file_util.call_args)
        # Checking that the os._exit method was called.
        patched_exit.assert_called_once_with(0)
        # Checking that the execution flow of the test was correct. The
        # original error is the side effect of load_setuptools_entrypoints.
        load_setuptools_entrypoints.assert_called_once()
