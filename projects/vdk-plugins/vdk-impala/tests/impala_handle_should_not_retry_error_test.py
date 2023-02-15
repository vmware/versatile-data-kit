# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import patch

from impala.error import OperationalError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaHandleShouldNotRetryErrorTest(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_query_timed_out_error(self, patched_time_sleep):
        error_message = "Query f145bbdb02d50678:9dd123a800000000 expired due to execution time limit of 1h"
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

        mock_native_cursor.execute.assert_not_called()
