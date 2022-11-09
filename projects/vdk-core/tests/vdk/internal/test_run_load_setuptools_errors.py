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
    @patch(
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFileAction.write_to_file"
    )
    def test_import_error(
        self,
        file_util: MagicMock,
        load_setuptools_entrypoints: MagicMock,
    ):
        """
        This test simulates a scenario where a user imports a library that
        has a clash with vdk internal imports. The desired behaviour is to
        terminate with user error.
        """
        with patch("sys.exit") as patched_exit:
            main()
            file_util.assert_called_once()
            assert '"status": "User error"' in str(file_util.call_args)
            # Checking that the execution flow of the test was correct. The
            # original error is the side effect of load_setuptools_entrypoints.
            load_setuptools_entrypoints.assert_called_once()
            # Testing exit status code.
            patched_exit.assert_called_once_with(1)

    @patch(
        "pluggy._manager.PluginManager.load_setuptools_entrypoints",
        side_effect=Exception("Test general error."),
    )
    @patch(
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFileAction.write_to_file"
    )
    def test_general_error(
        self,
        file_util: MagicMock,
        load_setuptools_entrypoints: MagicMock,
    ):
        """
        This test simulates a scenario where a general exception is thrown
        when running the load_setuptools_entrypoints method. The desired
        behavior is to log the exception and terminate with a Platform error.
        """
        with patch("sys.exit") as patched_exit:
            main()
            # WriteToFileAction.write_to_file() method which takes
            # the termination message as parameter. We check that
            # Exception resulted in platform error termination message.
            file_util.assert_called_once()
            assert '"status": "Platform error"' in str(file_util.call_args)
            # Checking that the execution flow of the test was correct. The
            # original error is the side effect of load_setuptools_entrypoints.
            load_setuptools_entrypoints.assert_called_once()
            # Testing exit status code.
            patched_exit.assert_called_once_with(1)
