# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import call
from unittest.mock import patch

from impala.error import HiveServer2Error
from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaMetadataExceptionWithInvalidateAndBackoff(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_OperationalError_TableLoadingException_error_loading_metadata_for_table(
        self, patched_time_sleep
    ):
        error_message = """TableLoadingException: Error loading metadata for table: eda_ps_dw.admin_log_refresh_dw
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager
Will issue invalidate metadata and try again."""
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

        expected_calls = [
            call("invalidate metadata eda_ps_dw.admin_log_refresh_dw"),
            call(self._query),
        ]
        mock_native_cursor.execute.assert_has_calls(expected_calls)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_HiveServer2Error_TableLoadingException_error_loading_metadata_for_table(
        self, patched_time_sleep
    ):
        error_message = """TableLoadingException: Error loading metadata for table: eda_ps_dw.admin_log_refresh_dw
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager
Will issue invalidate metadata and try again."""
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

        expected_calls = [
            call("invalidate metadata eda_ps_dw.admin_log_refresh_dw"),
            call(self._query),
        ]
        mock_native_cursor.execute.assert_has_calls(expected_calls)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_LocalCatalogException_could_not_load_table_from_metastore(
        self, patched_time_sleep
    ):
        error_message = """LocalCatalogException: Could not load table eda_peme_internal_dw.vw_ews_fmt from metastore
CAUSED BY: TException: TGetPartialCatalogObjectResponse(status:TStatus(status_code:GENERAL, error_msgs:[TableLoadingException: Failed to load metadata for table: eda_peme_internal_dw.vw_ews_fmt. Running 'invalidate metadata eda_peme_internal_dw.vw_ews_fmt' may resolve this problem.
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager]), lookup_status:OK)"""
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

        expected_calls = [
            call("invalidate metadata eda_peme_internal_dw.vw_ews_fmt"),
            call(self._query),
        ]
        mock_native_cursor.execute.assert_has_calls(expected_calls)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_AnalysisException_could_not_resolve_table_reference(
        self, patched_time_sleep
    ):
        error_message = "AnalysisException: Could not resolve table reference: 'test_schema.test_table'"
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

        expected_calls = [
            call("invalidate metadata test_schema.test_table"),
            call(self._query),
        ]
        mock_native_cursor.execute.assert_has_calls(expected_calls)


if __name__ == "__main__":
    unittest.main()
