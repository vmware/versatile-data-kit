# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest import mock
from unittest.mock import call
from unittest.mock import MagicMock

from utils import populate_mock_managed_cursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.internal.core import errors


class ManagedCursorTests(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"
        self._log = logging.getLogger()

    def test_validation__query_valid__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()

        mock_managed_cursor.execute(self._query)

        mock_connection_hook_spec.validate_operation.assert_called_once_with(
            operation=self._query, parameters=None
        )
        mock_native_cursor.execute.assert_called_once()

    def test_validation__query_nonvalid__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()
        mock_connection_hook_spec.validate_operation.side_effect = Exception(
            "Validation exception"
        )

        with self.assertRaises(Exception) as e:
            mock_managed_cursor.execute(self._query)

        self.assertEqual(e.exception.args[0], "Validation exception")
        mock_native_cursor.execute.assert_not_called()

    def test_decoration__success__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()

        def mock_decorate(decoration_cursor: DecorationCursor):
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation(
                f"decorated {managed_operation.get_operation()}"
            )

        mock_connection_hook_spec.decorate_operation.side_effect = mock_decorate

        mock_managed_cursor.execute(self._query)

        mock_connection_hook_spec.decorate_operation.assert_called_once()
        calls = [call(f"decorated {self._query}")]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_decoration__failure__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()
        mock_connection_hook_spec.decorate_operation.side_effect = Exception(
            "Decoration exception"
        )

        with self.assertRaises(Exception) as e:
            mock_managed_cursor.execute(self._query)

        self.assertTrue(mock_connection_hook_spec.decorate_operation.called)
        self.assertEqual(e.exception.args[0], "Decoration exception")
        mock_native_cursor.execute.assert_not_called()

    def test_recovery__success__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()

        def mock_decorate(decoration_cursor: DecorationCursor):
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation(
                f"decorated {managed_operation.get_operation()}"
            )

        def mock_recover(recovery_cursor: RecoveryCursor):
            recovery_cursor.execute("recovery")
            recovery_cursor.retry_operation()
            assert recovery_cursor.get_retries() == 1

        mock_connection_hook_spec.decorate_operation.side_effect = mock_decorate
        mock_connection_hook_spec.recover_operation.side_effect = mock_recover

        exception = Exception()
        mock_native_cursor.execute.side_effect = [exception, None, None]

        mock_managed_cursor.execute(self._query)

        mock_connection_hook_spec.recover_operation.assert_called_once()
        calls = [
            call(f"decorated {self._query}"),
            call(f"decorated recovery"),
            call(f"decorated {self._query}"),
        ]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_recovery__failure__execute(self):
        (
            mock_native_cursor,
            mock_managed_cursor,
            _,
            _,
            mock_connection_hook_spec,
        ) = populate_mock_managed_cursor()

        def mock_decorate(decoration_cursor: DecorationCursor):
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation(
                f"decorated {managed_operation.get_operation()}"
            )

        def mock_recover(recovery_cursor: RecoveryCursor):
            raise Exception("Could not handle execution exception")

        mock_connection_hook_spec.decorate_operation.side_effect = mock_decorate
        mock_connection_hook_spec.recover_operation.side_effect = mock_recover

        exception = Exception()
        mock_native_cursor.execute.side_effect = exception

        with self.assertRaises(Exception) as e:
            mock_managed_cursor.execute(self._query)

        self.assertEqual(e.exception.args[0], "Could not handle execution exception")
        mock_connection_hook_spec.recover_operation.assert_called_once()
        mock_native_cursor.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
