# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import Callable

from taurus.vdk.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from taurus.vdk.builtin_plugins.connection.managed_cursor import ManagedCursor
from taurus.vdk.builtin_plugins.connection.pep249.interfaces import PEP249Connection


class WrappedConnection(ManagedConnectionBase):
    """
    Wrap any DB connection ones (e.g. connection to SAP Hana) into a ManagedConnection
    """

    def _before_cursor_execute(self, cur: ManagedCursor) -> None:
        return super()._before_cursor_execute(cur)

    def _cursor_execute(self, cur: ManagedCursor, query: str) -> None:
        return super()._cursor_execute(cur, query)

    def __init__(
        self,
        log: logging.Logger,
        new_connection_builder_function: Callable[[], PEP249Connection],
    ) -> None:
        """
        :param new_connection_builder_function: method that returns a new (e.g. SAP Hana) connection
            Example
                def connection() -> ManagedConnectionBase:
                    db = pyhdb.connect(host='hana-prod-d1.northpole.com', port=30015, user='claus', password='hohoho')
                    return db

        """
        super().__init__(log)
        self._log = logging.getLogger(__name__)
        self._new_connection_builder_function = new_connection_builder_function

    def _connect(self) -> Any:
        self._log.debug("Establishing Wrapped connection ...")
        conn = self._new_connection_builder_function()
        self._log.debug("Establishing Wrapped connection DONE: %s", str(conn))
        return conn
