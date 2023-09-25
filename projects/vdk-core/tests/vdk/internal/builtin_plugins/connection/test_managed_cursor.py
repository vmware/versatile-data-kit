# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import call

import pytest
import structlog
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor

_query = "select 1"


def test_validation__query_valid__execute():
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_connection_hook_spec,
    ) = populate_mock_managed_cursor()

    mock_managed_cursor.execute(_query)

    mock_connection_hook_spec.db_connection_validate_operation.assert_called_once_with(
        operation=_query, parameters=None
    )
    mock_native_cursor.execute.assert_called_once()


def test_validation__query_nonvalid__execute():
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_connection_hook_spec,
    ) = populate_mock_managed_cursor()
    mock_connection_hook_spec.db_connection_validate_operation.side_effect = Exception(
        "Validation exception"
    )

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert "Validation exception" == e.value.args[0]
    mock_native_cursor.execute.assert_not_called()


def test_decoration__success__execute():
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

    mock_connection_hook_spec.db_connection_decorate_operation.side_effect = (
        mock_decorate
    )

    mock_managed_cursor.execute(_query)

    mock_connection_hook_spec.db_connection_decorate_operation.assert_called_once()
    calls = [call(f"decorated {_query}")]
    mock_native_cursor.execute.assert_has_calls(calls)


def test_decoration__failure__execute():
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_connection_hook_spec,
    ) = populate_mock_managed_cursor()
    mock_connection_hook_spec.db_connection_decorate_operation.side_effect = Exception(
        "Decoration exception"
    )

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert True == mock_connection_hook_spec.db_connection_decorate_operation.called
    assert "Decoration exception" == e.value.args[0]
    mock_native_cursor.execute.assert_not_called()


def test_recovery__success__execute():
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

    mock_connection_hook_spec.db_connection_decorate_operation.side_effect = (
        mock_decorate
    )
    mock_connection_hook_spec.db_connection_recover_operation.side_effect = mock_recover

    exception = Exception()
    mock_native_cursor.execute.side_effect = [exception, None, None]

    mock_managed_cursor.execute(_query)

    mock_connection_hook_spec.db_connection_recover_operation.assert_called_once()
    calls = [
        call(f"decorated {_query}"),
        call(f"decorated recovery"),
        call(f"decorated {_query}"),
    ]
    mock_native_cursor.execute.assert_has_calls(calls)


def test_recovery__failure__execute():
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

    mock_connection_hook_spec.db_connection_decorate_operation.side_effect = (
        mock_decorate
    )
    mock_connection_hook_spec.db_connection_recover_operation.side_effect = mock_recover

    exception = Exception()
    mock_native_cursor.execute.side_effect = exception

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert "Could not handle execution exception" == e.value.args[0]
    mock_connection_hook_spec.db_connection_recover_operation.assert_called_once()
    mock_native_cursor.execute.assert_called_once()


def test_query_timing_successful_query(caplog):
    caplog.set_level(logging.INFO)
    (
        _,
        mock_managed_cursor,
        _,
        _,
        _,
    ) = populate_mock_managed_cursor()
    mock_managed_cursor.execute(_query)
    assert "Query duration 00h:00m:" in str(caplog.records)


def test_query_timing_recovered_query(caplog):
    caplog.set_level(logging.INFO)
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        _,
    ) = populate_mock_managed_cursor()
    mock_native_cursor.execute.side_effect = [Exception("Mock exception")]
    mock_managed_cursor.execute(_query)
    assert "Recovered query duration 00h:00m:" in str(caplog.records)


def test_query_timing_failed_query(caplog):
    caplog.set_level(logging.INFO)
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_connection_hook_spec,
    ) = populate_mock_managed_cursor()

    exception = Exception("Mock exception")
    mock_native_cursor.execute.side_effect = [exception]
    mock_connection_hook_spec.db_connection_recover_operation.side_effect = [exception]
    with pytest.raises(Exception):
        mock_managed_cursor.execute(_query)

    assert "Failed query duration 00h:00m:" in str(caplog.records)
