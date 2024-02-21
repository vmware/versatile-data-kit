# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import List
from typing import Optional

from oracledb import Connection
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection

log = logging.getLogger(__name__)


class OracleConnection(ManagedConnectionBase):
    def __init__(
        self,
        user: str,
        password: str,
        connection_string: str = None,
        host=None,
        port=1521,
        sid: str = None,
        service_name: str = None,
        thick_mode: bool = True,
        thick_mode_lib_dir: Optional[str] = None,
    ):
        super().__init__(log)
        self._oracle_user = user
        self._oracle_password = password
        self._host = host
        self._port = port
        self._sid = sid
        self._service_name = service_name
        self._oracle_connection_string = connection_string
        self._thick_mode = thick_mode
        self._thick_mode_lib_dir = thick_mode_lib_dir

    def _connect(self) -> Connection:
        import oracledb

        if self._thick_mode:
            if self._thick_mode_lib_dir:
                oracledb.init_oracle_client(self._thick_mode_lib_dir)
            else:
                oracledb.init_oracle_client()
        if self._oracle_connection_string:
            log.debug("Connecting to Oracle using connection string")
            params = oracledb.ConnectParams()
            params.set(user=self._oracle_user)
            params.set(password=self._oracle_password)
            params.parse_connect_string(self._oracle_connection_string)

            conn = oracledb.connect(params=params)
        else:
            log.debug("Connecting to Oracle using host,port,sid")
            params = oracledb.ConnectParams(
                user=self._oracle_user,
                password=self._oracle_password,
                host=self._host,
                port=self._port,
                sid=self._sid,
                service_name=self._service_name,
            )
            conn = oracledb.connect(params=params)
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
