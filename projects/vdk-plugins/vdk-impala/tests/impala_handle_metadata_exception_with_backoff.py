# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import patch

from impala.error import HiveServer2Error
from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaMetadataExceptionWithBackoff(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_AnalysisException_could_not_resolve_column_field(self, patched_time_sleep):
        error_message = "AnalysisException: Could not resolve column/field reference: 'ss__src_arrival_ts'"
        exception = HiveServer2Error(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )
        error_handler.handle_error(
            caught_exception=exception, recovery_cursor=mock_recovery_cursor
        )

        mock_native_cursor.execute.assert_called_with(self._query)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_ImpalaRuntimeException_error_making_alter_table_rpc_to_hive(
        self, patched_time_sleep
    ):
        error_message = """ImpalaRuntimeException: Error making 'alter_table' RPC to Hive Metastore:
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager"""
        exception = OperationalError(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )
        error_handler.handle_error(
            caught_exception=exception, recovery_cursor=mock_recovery_cursor
        )

        mock_native_cursor.execute.assert_called_with(self._query)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_ImpalaRuntimeException_error_making_updateTableColumnStatistics(
        self, patched_time_sleep
    ):
        error_message = """ImpalaRuntimeException: Error making 'updateTableColumnStatistics' RPC to Hive Metastore:
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager"""
        exception = OperationalError(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )
        error_handler.handle_error(
            caught_exception=exception, recovery_cursor=mock_recovery_cursor
        )

        mock_native_cursor.execute.assert_called_with(self._query)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_ImpalaOutOfMemory_error(self, patched_time_sleep):
        error_message = "OutOfMemoryError: null"
        exception = HiveServer2Error(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )
        error_handler.handle_error(
            caught_exception=exception, recovery_cursor=mock_recovery_cursor
        )

        mock_native_cursor.execute.assert_called_with(self._query)


if __name__ == "__main__":
    unittest.main()
