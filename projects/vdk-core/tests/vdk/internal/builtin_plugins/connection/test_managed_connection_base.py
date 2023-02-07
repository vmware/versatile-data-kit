# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Tuple
from unittest.mock import MagicMock

import pytest
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    ConnectionHookSpecFactory,
)
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Cursor

log = logging.getLogger(__name__)


def test_new_pep249_connnection():
    managed_conn, mock_raw_conn = get_test_managed_and_raw_connection()
    assert managed_conn.connect() == mock_raw_conn
    assert managed_conn._is_connected()


def test_execute_query():
    managed_conn, mock_raw_conn = get_test_managed_and_raw_connection()
    managed_conn.execute_query("select 1")

    mock_raw_conn.cursor.assert_any_call()
    assert managed_conn._is_connected()


def test_execute_query_fail():
    managed_conn, mock_raw_conn = get_test_managed_and_raw_connection()
    mock_raw_conn.cursor.side_effect = SyntaxError("foo")
    with pytest.raises(SyntaxError):
        managed_conn.execute_query("select 1")

    # also connection check (select 1) should return False
    assert not managed_conn._is_connected()


def test_execute_query_fail_to_fetch():
    managed_conn, mock_raw_conn = get_test_managed_and_raw_connection()
    mock_cursor = MagicMock(spec=PEP249Cursor)
    mock_raw_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.side_effect = SyntaxError("foo")
    with pytest.raises(SyntaxError):
        managed_conn.execute_query("select 1")


def test_execute_close_reopen():
    managed_conn, mock_raw_conn = get_test_managed_and_raw_connection()

    managed_conn.close()
    assert not managed_conn._is_connected()

    managed_conn.connect()
    assert managed_conn._is_connected()


def get_test_managed_and_raw_connection() -> (
    Tuple[ManagedConnectionBase, PEP249Connection]
):
    mock_conn = MagicMock(spec=PEP249Connection)
    connection_hook_spec_factory = MagicMock(spec=ConnectionHookSpecFactory)
    connection_hook_spec_factory.get_connection_hook_spec.return_value = MagicMock()

    class ConcretePEP249Connection(ManagedConnectionBase):
        def _connect(self) -> PEP249Connection:
            return mock_conn

    conn = ConcretePEP249Connection(log, None, connection_hook_spec_factory)
    return conn, mock_conn
