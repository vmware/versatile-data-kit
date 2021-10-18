# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

from vdk.api.plugin.connection_hook_spec import (
    ConnectionHookSpec,
)
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.decoration_cursor import ManagedOperation
from vdk.internal.builtin_plugins.connection.managed_cursor import ManagedCursor
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor
from vdk.internal.builtin_plugins.connection.recovery_cursor import RecoveryCursor


def populate_mock_managed_cursor(
    mock_exception_to_recover=None, mock_operation=None, mock_parameters=None
) -> (
    PEP249Cursor,
    ManagedCursor,
    DecorationCursor,
    RecoveryCursor,
    ConnectionHookSpec,
):
    import logging

    managed_operation = ManagedOperation(mock_operation, mock_parameters)
    mock_connection_hook_spec = MagicMock(spec=ConnectionHookSpec)
    mock_native_cursor = MagicMock(spec=PEP249Cursor)

    managed_cursor = ManagedCursor(
        cursor=mock_native_cursor,
        log=logging.getLogger(),
        connection_hook_spec=mock_connection_hook_spec,
    )

    decoration_cursor = DecorationCursor(mock_native_cursor, None, managed_operation)

    return (
        mock_native_cursor,
        managed_cursor,
        decoration_cursor,
        RecoveryCursor(
            native_cursor=mock_native_cursor,
            log=logging.getLogger(),
            exception=mock_exception_to_recover,
            managed_operation=managed_operation,
            decoration_operation_callback=mock_connection_hook_spec.decorate_operation,
        ),
        mock_connection_hook_spec,
    )
