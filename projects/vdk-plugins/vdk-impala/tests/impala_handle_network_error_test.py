# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import patch

from impala.error import HiveServer2Error
from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaHandleNetworkErrorTest(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_query_is_retried(self, patched_time_sleep):
        error_message = "Network error"
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
    def test_TransmitData_error(self, patched_time_sleep):
        error_message = "TransmitData() to 10.153.201.38:27000 failed: Network error: recv error: Connection reset by peer (error 104)"
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
    def test_connection_refused(self, patched_time_sleep):
        error_message = "ExecQueryFInstances rpc query_id=3744fec98403153b:5a72fd6b00000000 failed: RPC client failed to connect: Couldn't open transport for ph-hdp-prd-dn01.vac.vmware.com:22000 (connect() failed: Connection refused)"
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
    def test_unreachable_impalad(self, patched_time_sleep):
        error_message = "Cancelled due to unreachable impalad(s): ph-hdp-prd-dn23.vac.vmware.com:22000"
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
    def test_unstable_connection_impalad_hdfs(self, patched_time_sleep):
        error_message = (
            "An exception occurred, exception message was: "
            "ImpalaRuntimeException: Unable to call create UDF instance.\n"
            "CAUSED BY: InvocationTargetException: null\nCAUSED BY: IOException: Stream closed"
        )
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
    def test_failed_to_connect(self, patched_time_sleep):
        error_message = "Failed after retrying 3 times"
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
