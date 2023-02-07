# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from unittest.mock import call
from unittest.mock import patch

from impala.error import HiveServer2Error
from vdk.plugin.impala.impala_error_handler import ImpalaErrorHandler
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor


@patch("time.sleep", return_value=None)
def test_AnalysisException_could_not_resolve_table_reference(patched_time_sleep):
    _query = "select 1"
    error_message = "AnalysisException: Table does not exist: test_schema.test_table"
    exception = HiveServer2Error(error_message)

    error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
    (
        mock_native_cursor,
        _,
        _,
        mock_recovery_cursor,
        _,
    ) = populate_mock_managed_cursor(
        mock_exception_to_recover=exception, mock_operation=_query
    )
    error_handler.handle_error(
        caught_exception=exception, recovery_cursor=mock_recovery_cursor
    )

    expected_calls = [
        call("invalidate metadata test_schema.test_table"),
        call(_query),
    ]
    mock_native_cursor.execute.assert_has_calls(expected_calls)


@patch("time.sleep", return_value=None)
def test_AlreadyExistsException_table_already_exists(patched_time_sleep):
    error_message = "AlreadyExistsException: Table test_table already exists"
    exception = HiveServer2Error(error_message)
    original_query = "CREATE TABLE test_schema.test_table AS SELECT * FROM test_mart.view_test_table;"
    (
        mock_native_cursor,
        _,
        _,
        mock_recovery_cursor,
        _,
    ) = populate_mock_managed_cursor(
        mock_exception_to_recover=exception, mock_operation=original_query
    )

    error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
    error_handler.handle_error(
        caught_exception=exception, recovery_cursor=mock_recovery_cursor
    )

    expected_calls = [
        call("invalidate metadata test_schema.test_table"),
        call(original_query),
    ]
    mock_native_cursor.execute.assert_has_calls(expected_calls)


@patch("time.sleep", return_value=None)
def test_AlreadyExistsException_view_already_exists(patched_time_sleep):
    error_message = "AlreadyExistsException: Table test_table already exists"
    exception = HiveServer2Error(error_message)
    original_query = (
        "CREATE VIEW test_schema.test_table AS "
        "SELECT * "
        "FROM test_mart.view_test_table;"
    )
    (mock_native_cursor, _, _, mock_recovery_cursor, _) = populate_mock_managed_cursor(
        mock_exception_to_recover=exception, mock_operation=original_query
    )

    error_handler = ImpalaErrorHandler(logging.getLogger(), num_retries=1)
    error_handler.handle_error(
        caught_exception=exception, recovery_cursor=mock_recovery_cursor
    )

    expected_calls = [
        call("invalidate metadata test_schema.test_table"),
        call(original_query),
    ]
    mock_native_cursor.execute.assert_has_calls(expected_calls)
