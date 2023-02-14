# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest.mock import patch

import pytest
from impala.error import OperationalError
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
class ImpalaHandlePoolError(unittest.TestCase):
    def setUp(self):
        self._query = "select 1"

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_OperationalError_rejected_pool_error(self, patched_time_sleep):
        error_message = "impala.error.operationalerror: rejected pool root.starshot: queue full, limit=, num_queued=."
        exception = OperationalError(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        _, _, _, mock_recovery_cursor, _ = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )

        with pytest.raises(UserCodeError):
            error_handler.handle_error(
                caught_exception=exception, recovery_cursor=mock_recovery_cursor
            )

    # do not remove patched_time_sleep, it's used by @patch('time.sleep', return_value=None)
    def test_OperationalError_admission_for_timeout_error(self, patched_time_sleep):
        error_message = "impala.error.operationalerror: admission for timeout ms in pool root.data-jobs. queued reason: queu"
        exception = OperationalError(error_message)

        error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
        _, _, _, mock_recovery_cursor, _ = populate_mock_managed_cursor(
            mock_exception_to_recover=exception, mock_operation=self._query
        )

        with pytest.raises(UserCodeError):
            error_handler.handle_error(
                caught_exception=exception, recovery_cursor=mock_recovery_cursor
            )
