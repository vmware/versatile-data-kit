# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import call
from unittest.mock import patch

import impala
from impala.error import HiveServer2Error
from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaErrorHandlerTest(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"
        self.error_handler = ImpalaErrorHandler(log=logging.getLogger())

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_default_retry(self, patched_time_sleep):
        test_exception = OperationalError(
            "Network error"
        )  # we know for sure this is handled
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = test_exception

        self.assertFalse(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        calls = [call(self._query)] * 5
        mock_native_cursor.execute.assert_has_calls(calls)

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_custom_retry(self, patched_time_sleep):
        test_exception = OperationalError(
            "Network error"
        )  # we know for sure this is handled
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = test_exception

        error_handler = ImpalaErrorHandler(log=logging.getLogger(), num_retries=3)
        self.assertFalse(
            error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        calls = [call(self._query)] * 3
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_table_already_exists_happy_path(self, patched_time_sleep):
        test_exception = impala.error.HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME"
        )
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )

        self.assertTrue(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        calls = [call("invalidate metadata db.TABLE_NAME"), call(self._query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_table_already_exists_retry_only_once(self, patched_time_sleep):
        test_exception = impala.error.HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME"
        )
        # first we execute query with fix and 2nd we re-try original query - we will fail with same error
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = [None, test_exception]

        self.assertFalse(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        self.assertEqual(2, mock_native_cursor.execute.call_count)
        calls = [call("invalidate metadata db.TABLE_NAME"), call(self._query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_table_already_exists_handled_by_other_handler(
        self, patched_time_sleep
    ):
        original_exception_fixed_by_other_handler = OperationalError("Network error")
        test_exception = HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME"
        )
        # after network error retry we throw Table does not exist which should be handled
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=original_exception_fixed_by_other_handler,
            mock_operation=self._query,
        )
        mock_native_cursor.execute.side_effect = [test_exception, None, ...]

        self.assertTrue(
            self.error_handler.handle_error(
                original_exception_fixed_by_other_handler, mock_recovery_cursor
            )
        )

        calls = [call("invalidate metadata db.TABLE_NAME"), call(self._query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_table_already_exists_new_exception_is_thrown_after_fix(
        self, patched_time_sleep
    ):
        new_exception = AttributeError("foo")
        test_exception = HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME"
        )

        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = [None, new_exception]

        # after invalidate metadata , original query fail again but with new exception
        with self.assertRaises(AttributeError):
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)

        # make sure we have tried
        calls = [call("invalidate metadata db.TABLE_NAME"), call(self._query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_could_not_load_table(self, patched_time_sleep):
        msg = """impala.error.HiveServer2Error: LocalCatalogException: Could not load table vsphere_health_check_dashboard._click_n_fix from metastore
CAUSED BY: TException: TGetPartialCatalogObjectResponse(status:TStatus(status_code:GENERAL, error_msgs:[TableLoadingException: Failed to load metadata for table: vsphere_health_check_dashboard._click_n_fix. Running 'invalidate metadata vsphere_health_check_dashboard._click_n_fix' may resolve this problem.
CAUSED BY: MetaException: Object with id "" is managed by a different persistence manager]), lookup_status:OK)"""
        test_exception = HiveServer2Error(msg)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )

        self.assertTrue(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        calls = [
            call("invalidate metadata vsphere_health_check_dashboard._click_n_fix"),
            call(self._query),
        ]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_invalidate_metadata_two_different_tables(self, patched_time_sleep):
        test_exception_table_1 = impala.error.HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME_1"
        )
        test_exception_table_2 = impala.error.HiveServer2Error(
            "AnalysisException: Table does not exist: db.TABLE_NAME_2"
        )
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception_table_1, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = [
            None,
            test_exception_table_2,
            None,
            ...,
        ]

        self.assertTrue(
            self.error_handler.handle_error(
                test_exception_table_1, mock_recovery_cursor
            )
        )

        calls = [call("invalidate metadata db.TABLE_NAME_1"), call(self._query)]
        calls += [call("invalidate metadata db.TABLE_NAME_2"), call(self._query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_handle_should_not_retry_error(self, patched_time_sleep):
        test_exception = OperationalError(
            "Query 9a467f0c5086b6fd:6ef6fc200000000 expired due to execution time limit of 1h"
        )
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        # we must not re-try but re-raise caught exception.
        self.assertFalse(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )
        mock_native_cursor.execute.assert_not_called()

    def test_handle_failed_to_open_hdfs_new_authorization_exception_is_thrown_after_fix(
        self, patched_time_sleep
    ):
        new_exception = HiveServer2Error(
            "AuthorizationException: User 'pa__view_test-user' does not have privileges to "
            "execute 'INVALIDATE METADATA/REFRESH' on"
        )
        test_exception = OperationalError(
            """Disk I/O error: Failed to open HDFS file
            hdfs://HDFS/user/hive/warehouse/history.db/vm/pa__arrival_day=1573171200/pa__collector_id=vSphere.6_6/pa__schema_version=1/7642f6c1c2c31372-588d054900000012_186717772_data.0.parq
            Error(255): Unknown error 255
            Root cause: ConnectException: Connection refused"""
        )
        original_query = "select * from history.vm"

        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=original_query
        )
        mock_native_cursor.execute.side_effect = [new_exception, None]

        self.error_handler.handle_error(test_exception, mock_recovery_cursor)

        # make sure we have tried
        calls = [call("refresh `history`.`vm`"), call(original_query)]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_memory_error(self, patched_time_sleep):
        msg = """Memory limit exceeded: HdfsParquetTableWriter::BaseColumnWriter::Flush() failed to allocate 884879 bytes for dictionary page.
HdfsTableSink could not allocate 864.14 KB without exceeding limit.
Error occurred on backend prd-impala-wdc-08-vc24c06-e14-ix-2.supercollider.vmware.com:22000 by fragment 0842bccde0974578:6fd468a200000042
Memory left in process limit: 116.53 GB
Memory left in query limit: 640.67 KB
Query(0842bccde0974578:6fd468a200000000): Limit=2.00 GB Reservation=1.78 GB ReservationLimit=9.00 GB OtherMemory=227.37 MB Total=2.00 GB Peak=2.00 GB
  Fragment 0842bccde0974578:6fd468a200000042: Reservation=1.78 GB OtherMemory=227.37 MB Total=2.00 GB Peak=2.00 GB"""
        test_exception = OperationalError(msg)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=test_exception, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = [
            None,
            test_exception,
            None,
            test_exception,
            None,
            test_exception,
            None,
            test_exception,
            None,
            ...,
        ]

        self.assertTrue(
            self.error_handler.handle_error(test_exception, mock_recovery_cursor)
        )

        calls = [
            call("set mem_limit=2576980377;"),
            call("select 1"),
            call("set mem_limit=3221225472;"),
            call("select 1"),
            call("set mem_limit=4294967296;"),
            call("select 1"),
            call("set memory_limit=512GB;"),
            call("select 1"),
            call("select 1"),
        ]

        mock_native_cursor.execute.assert_has_calls(calls)


if __name__ == "__main__":
    unittest.main()
