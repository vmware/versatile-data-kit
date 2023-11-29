# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import List

from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection

log = logging.getLogger(__name__)


class OracleConnection(ManagedConnectionBase):
    def __init__(self, user: str, password: str, connection_string: str):
        super().__init__(log)
        self._oracle_user = user
        self._oracle_password = password
        self._oracle_connection_string = connection_string

    def _connect(self) -> PEP249Connection:
        import oracledb

        conn = oracledb.connect(
            user=self._oracle_user,
            password=self._oracle_password,
            dsn=self._oracle_connection_string,
        )
        return conn

    def _is_connected(self) -> bool:
        if None is self._is_db_con_open:
            return False
        if False is self._is_db_con_open:
            return False
        try:
            """
            The remote end (the database server) may have disconnected or the session may have timed out (on the remote one)
            but in the client (here in vdk - we are the client) we do not know.
            We try to check with "select count(*) from user_tables where rownum = 1".
            Note: The default behavior is to just use "select 1", but this didn't work for Oracle
            """
            self._cursor().execute("select count(*) from user_tables where rownum = 1")
            return True
        except Exception as e:
            self._log.debug(
                f"Connection {self} is disconnected ('select 1' returned {e})"
            )
        return False

    def execute_query(self, query: str) -> List[List[Any]]:
        try:
            return super().execute_query(query)
        finally:
            self.commit()
