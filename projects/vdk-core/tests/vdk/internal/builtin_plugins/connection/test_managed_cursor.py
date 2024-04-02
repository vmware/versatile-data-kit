# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Container
from typing import Optional
from unittest.mock import call
from unittest.mock import Mock

import pytest
from vdk.internal.builtin_plugins.connection.database_managed_connection import (
    IDatabaseManagedConnection,
)
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.execution_cursor import (
    ExecuteOperationResult,
)
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor
from vdk.plugin.test_utils.util_funcs import populate_mock_managed_cursor_no_hook

_query = "select 1"


class ManagedDatabaseConnectionTestImpl(IDatabaseManagedConnection):
    def db_connection_validate_operation(
        self, operation: str, parameters: Optional[Container]
    ) -> None:
        print("Validate called not from Base class")

    def db_connection_decorate_operation(
        self, decoration_cursor: DecorationCursor
    ) -> None:
        print("Decorate called not from Base class")

    def db_connection_execute_operation(
        self, execution_cursor: ExecutionCursor
    ) -> Optional[ExecuteOperationResult]:
        print("Execute called not from Base class")

    def db_connection_recover_operation(self, recovery_cursor: RecoveryCursor) -> None:
        print("Recover called not from Base class")

    def db_connection_after_operation(
        self, execution_cursor: ExecutionCursor
    ) -> Optional[ExecuteOperationResult]:
        print("After called")


@pytest.fixture
def managed_connection():
    return ManagedDatabaseConnectionTestImpl()


def test_no_hook_db_validate_operations(managed_connection):
    managed_connection.db_connection_validate_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    mock_managed_cursor.execute(_query)

    mock_managed_connection.db_connection_validate_operation.assert_called_once_with(
        operation=_query, parameters=None
    )

    mock_native_cursor.execute.assert_called_once()


def test_no_hook_validation__query_nonvalid__execute(managed_connection):
    managed_connection.db_connection_validate_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    mock_managed_connection.db_connection_validate_operation.side_effect = Exception(
        "Validation exception"
    )

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert "Validation exception" == e.value.args[0]
    mock_native_cursor.execute.assert_not_called()


def test_no_hook_decoration__success__execute(managed_connection):
    managed_connection.db_connection_decorate_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    def mock_decorate(decoration_cursor: DecorationCursor):
        managed_operation = decoration_cursor.get_managed_operation()
        managed_operation.set_operation(
            f"decorated {managed_operation.get_operation()}"
        )

    mock_managed_connection.db_connection_decorate_operation.side_effect = mock_decorate

    mock_managed_cursor.execute(_query)

    mock_managed_connection.db_connection_decorate_operation.assert_called_once()
    calls = [call(f"decorated {_query}")]
    mock_native_cursor.execute.assert_has_calls(calls)


def test_no_hook_decoration__failure__execute(managed_connection):
    managed_connection.db_connection_decorate_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    mock_managed_connection.db_connection_decorate_operation.side_effect = Exception(
        "Decoration exception"
    )

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert True == mock_managed_connection.db_connection_decorate_operation.called
    assert "Decoration exception" == e.value.args[0]
    mock_native_cursor.execute.assert_not_called()


def test_no_hook_recovery__success__execute(managed_connection):
    managed_connection.db_connection_decorate_operation = Mock()
    managed_connection.db_connection_recover_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    def mock_decorate(decoration_cursor: DecorationCursor):
        managed_operation = decoration_cursor.get_managed_operation()
        managed_operation.set_operation(
            f"decorated {managed_operation.get_operation()}"
        )

    def mock_recover(recovery_cursor: RecoveryCursor):
        recovery_cursor.execute("recovery")
        recovery_cursor.retry_operation()
        assert recovery_cursor.get_retries() == 1

    mock_managed_connection.db_connection_decorate_operation.side_effect = mock_decorate
    mock_managed_connection.db_connection_recover_operation.side_effect = mock_recover

    exception = Exception()
    mock_native_cursor.execute.side_effect = [exception, None, None]

    mock_managed_cursor.execute(_query)

    mock_managed_connection.db_connection_recover_operation.assert_called_once()
    calls = [
        call(f"decorated {_query}"),
        call(f"decorated recovery"),
        call(f"decorated {_query}"),
    ]
    mock_native_cursor.execute.assert_has_calls(calls)


def test_no_hook_recovery__failure__execute(managed_connection):
    managed_connection.db_connection_decorate_operation = Mock()
    managed_connection.db_connection_recover_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    def mock_decorate(decoration_cursor: DecorationCursor):
        managed_operation = decoration_cursor.get_managed_operation()
        managed_operation.set_operation(
            f"decorated {managed_operation.get_operation()}"
        )

    def mock_recover(recovery_cursor: RecoveryCursor):
        raise Exception("Could not handle execution exception")

    mock_managed_connection.db_connection_decorate_operation.side_effect = mock_decorate
    mock_managed_connection.db_connection_recover_operation.side_effect = mock_recover

    exception = Exception()
    mock_native_cursor.execute.side_effect = exception

    with pytest.raises(Exception) as e:
        mock_managed_cursor.execute(_query)

    assert "Could not handle execution exception" == e.value.args[0]
    mock_managed_connection.db_connection_recover_operation.assert_called_once()
    mock_native_cursor.execute.assert_called_once()


def test_db_after_operations(managed_connection):
    managed_connection.db_connection_after_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    mock_managed_cursor.execute(_query)

    mock_native_cursor.execute.assert_called_once()
    mock_managed_connection.db_connection_after_operation.assert_called_once()


def test_query_timing_successful_query(caplog, managed_connection):
    caplog.set_level(logging.INFO)
    (
        _,
        mock_managed_cursor,
        _,
        _,
        _,
    ) = populate_mock_managed_cursor_no_hook()
    mock_managed_cursor.execute(_query)
    assert "Query duration 00h:00m:" in str(caplog.records)


def test_query_timing_recovered_query(caplog, managed_connection):
    caplog.set_level(logging.INFO)
    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )
    mock_native_cursor.execute.side_effect = [Exception("Mock exception")]
    mock_managed_cursor.execute(_query)
    assert "Recovered query duration 00h:00m:" in str(caplog.records)


def test_query_timing_failed_query(caplog, managed_connection):
    caplog.set_level(logging.INFO)
    managed_connection.db_connection_recover_operation = Mock()

    (
        mock_native_cursor,
        mock_managed_cursor,
        _,
        _,
        mock_managed_connection,
    ) = populate_mock_managed_cursor_no_hook(
        managed_database_connection=managed_connection
    )

    exception = Exception("Mock exception")
    mock_native_cursor.execute.side_effect = [exception]
    mock_managed_connection.db_connection_recover_operation.side_effect = [exception]
    with pytest.raises(Exception):
        mock_managed_cursor.execute(_query)

    assert "Failed query duration 00h:00m:" in str(caplog.records)
