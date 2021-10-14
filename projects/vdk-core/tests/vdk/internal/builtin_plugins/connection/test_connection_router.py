# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

import pytest
from vdk.internal.builtin_plugins.connection.connection_hook_spec import (
    ConnectionHookSpec,
)
from vdk.internal.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.core.config import Configuration
from vdk.internal.core.errors import VdkConfigurationError


def managed_connection_router():
    conf = MagicMock(spec=Configuration)
    mock_conn = MagicMock(spec=PEP249Connection)

    class TestManagedConnection(ManagedConnectionBase):
        def _connect(self) -> PEP249Connection:
            return mock_conn

    router = ManagedConnectionRouter(conf, MagicMock(spec=ConnectionHookSpec))
    router.add_open_connection_factory_method(
        "TEST_DB", lambda: TestManagedConnection()
    )
    return router, mock_conn, conf


def test_router_open_connection():
    router, mock_conn, _ = managed_connection_router()

    conn = router.open_connection("TEST_DB")
    assert mock_conn == conn.connect()


def test_router_raw_connection():
    conf = MagicMock(spec=Configuration)
    router = ManagedConnectionRouter(conf, MagicMock(spec=ConnectionHookSpec))

    mock_conn = MagicMock(spec=PEP249Connection)
    router.add_open_connection_factory_method("RAW_DB", lambda: mock_conn)

    conn = router.open_connection("RAW_DB")
    assert mock_conn == conn.connect()


def test_router_open_connection_closed():
    router, mock_conn, _ = managed_connection_router()

    conn = router.open_connection("TEST_DB")
    conn.close()
    conn = router.open_connection("TEST_DB")
    assert mock_conn == conn.connect()


def test_router_no_such_connection():
    router, mock_conn, _ = managed_connection_router()

    with pytest.raises(VdkConfigurationError):
        router.open_connection("NO_SUCH")


def test_router_open_default_connection():
    router, mock_conn, mock_conf = managed_connection_router()
    mock_conf.get_value.return_value = "TEST_DB"
    conn = router.open_default_connection()
    assert mock_conn == conn.connect()


def test_router_open_default_connection_no_conf():
    router, mock_conn, mock_conf = managed_connection_router()
    mock_conf.get_value.return_value = None
    conn = router.open_default_connection()
    assert mock_conn == conn.connect()
