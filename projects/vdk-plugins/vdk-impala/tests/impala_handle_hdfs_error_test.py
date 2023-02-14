# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import call
from unittest.mock import MagicMock

from impala.error import HiveServer2Error
from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


class ImpalaHandleHdfsErrorTest(unittest.TestCase):
    def setUp(self):
        error_message = """Disk I/O error: Failed to open HDFS file hdfs://HDFS/user/hive/warehouse/history.db/vm/pa__arrival_day=1573171200/pa__collector_id=vSphere.6_6/pa__schema_version=1/7642f6c1c2c31372-588d054900000012_186717772_data.0.parq
Error(255): Unknown error 255
Root cause: ConnectException: Connection refused"""
        self._failed_to_open_exception = OperationalError(error_message)
        self._query = "select 1"

    def test_handle_hdfs_failed_to_open(self):
        error_handler = ImpalaErrorHandler(MagicMock())
        original_query = "select * from history.vm"

        def mock_decoration(decoration_cursor):
            decoration_cursor.execute("SET REQUEST_POOL='root.data-jobs'")
            managed_operation = decoration_cursor.get_managed_operation()
            managed_operation.set_operation(
                "\n".join(
                    [
                        "-- job_name: example-job-name",
                        "-- op_id: op_id_example",
                        "{operation}",
                    ]
                ).format(operation=managed_operation.get_operation())
            )

        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=self._failed_to_open_exception,
            mock_operation=original_query,
            decoration_operation_callback=mock_decoration,
        )

        error_handler.handle_error(self._failed_to_open_exception, mock_recovery_cursor)

        calls = [
            call("SET REQUEST_POOL='root.data-jobs'"),
            call(
                "-- job_name: example-job-name\n-- op_id: op_id_example\nrefresh `history`.`vm`"
            ),
            call(original_query),
        ]
        mock_native_cursor.execute.assert_has_calls(calls)

    def test_handle_hdfs_failed_to_open_and_refresh_failed(self):
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=self._failed_to_open_exception,
            mock_operation=self._query,
        )
        mock_native_cursor.execute.side_effect = [HiveServer2Error("foo")]

        error_handler = ImpalaErrorHandler(MagicMock())
        with self.assertRaises(HiveServer2Error):
            error_handler.handle_error(
                self._failed_to_open_exception, mock_recovery_cursor
            )

    def test_handle_error(self):
        exception = OperationalError("impala.error.OperationalError: MemoryLimit")
        error_handler = ImpalaErrorHandler(MagicMock())
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )
        # This test was changed because it started failing due to a change of the Impala error handling, which was
        # introduced with the commit below, where a specific types of Impala errors are now classified as user errors
        # and no longer raise exceptions.
        # https://gitlab.eng.vmware.com/product-analytics/data-pipelines/vdk/-/commit/1104585c06ac024b256626d4193228e0ab9f9f0f
        error_handler.handle_error(exception, mock_recovery_cursor)
        mock_native_cursor.execute.assert_called_once()

    def test_two_different_exceptions(self):
        initial_message = """Disk I/O error on hdp-prd-cdh6-ix15.supercollider.vmware.com:22000: Failed to open HDFS file hdfs://l3-vac.wdc-03-isi02.oc.vmware.com:8020/user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq
Error(2): No such file or directory
Root cause: RemoteException: Path name not found: /user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq"""
        initial_error = OperationalError(initial_message)
        secondary_error = HiveServer2Error(
            "AnalysisException: Table already exists: ..."
        )
        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=initial_error, mock_operation=self._query
        )

        mock_native_cursor.execute.side_effect = secondary_error

        with self.assertRaises(HiveServer2Error) as exc:
            error_handler.handle_error(
                caught_exception=initial_error, recovery_cursor=mock_recovery_cursor
            )
        assert exc.exception.args == secondary_error.args

    def test_two_same_exceptions_different_args(self):
        initial_message = """Disk I/O error on hdp-prd-cdh6-ix15.supercollider.vmware.com:22000: Failed to open HDFS file hdfs://l3-vac.wdc-03-isi02.oc.vmware.com:8020/user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq
Error(2): No such file or directory
Root cause: RemoteException: Path name not found: /user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq"""
        initial_error = OperationalError(initial_message)
        secondary_error = OperationalError(
            "Another Disk I/O error on hdp-prd-cdh6-ix15.supercollider.vmware.com:22000: occurred"
        )
        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=initial_error, mock_operation=self._query
        )

        mock_native_cursor.execute.side_effect = secondary_error

        with self.assertRaises(OperationalError) as exc:
            error_handler.handle_error(
                caught_exception=initial_error, recovery_cursor=mock_recovery_cursor
            )
        assert exc.exception.args == secondary_error.args

    def test_two_same_exceptions(self):
        error_message = """Disk I/O error on hdp-prd-cdh6-ix15.supercollider.vmware.com:22000: Failed to open HDFS file hdfs://l3-vac.wdc-03-isi02.oc.vmware.com:8020/user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq
Error(2): No such file or directory
Root cause: RemoteException: Path name not found: /user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq"""
        initial_error = OperationalError(error_message)
        secondary_error = OperationalError(error_message)
        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=initial_error, mock_operation=self._query
        )

        mock_native_cursor.execute.side_effect = secondary_error
        self.assertFalse(
            error_handler.handle_error(
                caught_exception=initial_error, recovery_cursor=mock_recovery_cursor
            )
        )

    def test_initial_exception_handled(self):
        error_message = """Disk I/O error on hdp-prd-cdh6-ix15.supercollider.vmware.com:22000: Failed to open HDFS file hdfs://l3-vac.wdc-03-isi02.oc.vmware.com:8020/user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq
Error(2): No such file or directory
Root cause: RemoteException: Path name not found: /user/hive/warehouse/starshot_csp_jira_dw.db/csp_customfieldoption/554fce0f545e17a0-739e2bfa0000006f_954094502_data.0.parq"""
        initial_error = OperationalError(error_message)
        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        _, _, _, mock_recovery_cursor, _ = populate_mock_managed_cursor(
            mock_exception_to_recover=initial_error, mock_operation=self._query
        )

        self.assertTrue(
            error_handler.handle_error(
                caught_exception=initial_error, recovery_cursor=mock_recovery_cursor
            )
        )

    def test_two_same_exceptions_no_args(self):
        initial_error = OperationalError()
        secondary_error = OperationalError()
        assert initial_error.args == secondary_error.args

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        (
            mock_native_cursor,
            _,
            _,
            mock_recovery_cursor,
            _,
        ) = populate_mock_managed_cursor(
            mock_exception_to_recover=initial_error, mock_operation=self._query
        )
        mock_native_cursor.execute.side_effect = secondary_error

        self.assertFalse(
            error_handler.handle_error(
                caught_exception=initial_error, recovery_cursor=mock_recovery_cursor
            )
        )


if __name__ == "__main__":
    unittest.main()
