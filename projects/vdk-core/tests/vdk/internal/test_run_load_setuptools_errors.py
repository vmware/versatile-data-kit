# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.internal.cli_entry import main
from vdk.internal.core.errors import clear_intermediate_errors


class TestImportErrors(unittest.TestCase):
    def setUp(self) -> None:
        # Clear logged and recorded error state before every test.
        clear_intermediate_errors()

    @patch(
        "pluggy._manager.PluginManager.load_setuptools_entrypoints",
        side_effect=ImportError("Test import error."),
    )
    @patch(
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFile"
        "Action.write_to_file"
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
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFile"
        "Action.write_to_file"
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

    @patch(
        "pluggy._manager.PluginManager.load_setuptools_entrypoints",
        side_effect=Exception("Test general error."),
    )
    @patch("vdk.internal.cli_entry.build_configuration")
    @patch(
        "vdk.internal.builtin_plugins.termination_message.file_util.WriteToFile"
        "Action.write_to_file"
    )
    @patch("vdk.internal.cli_entry.build_core_context_and_initialize")
    def test_hooks_called(
        self,
        build_core_context_and_initialize: MagicMock,
        termination_message_writer: MagicMock,
        build_configuration: MagicMock,
        setuptools_entrypoints: MagicMock,
    ):
        """
        This test checks if core initialization methods are called when
        the load_setuptools_entrypoints fails with an exception in the
        cli_entry.main() method.
        :param build_core_context_and_initialize: mocked real method
        :param termination_message_writer: mocked real method
        :param build_configuration: mocked real method
        :param setuptools_entrypoints: mocked real method with Exception side
        effect
        """
        with patch("sys.exit") as patched_exit:
            main()

            build_core_context_and_initialize.assert_called_once()
            termination_message_writer.assert_called_once()
            build_configuration.assert_called_once()
            setuptools_entrypoints.assert_called_once()
            patched_exit.assert_called_once_with(1)
