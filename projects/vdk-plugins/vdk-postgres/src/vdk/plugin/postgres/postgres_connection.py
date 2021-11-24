# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import List
from typing import Optional

from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)

_log = logging.getLogger(__name__)


class PostgresConnection(ManagedConnectionBase):
    def __init__(
        self,
        dsn: str = None,
        connection_factory=None,
        cursor_factory=None,
        dbname: str = None,
        # database - deprecated alias
        user: str = None,
        password: str = None,
        host: str = None,
        port: int = None,
        **kwargs,
    ):
        r"""
        See https://www.psycopg.org/docs/module.html
        Create a new database connection.

        The connection parameters can be specified as a string:

            conn = psycopg2.connect("dbname=test user=postgres password=secret")

        or using a set of keyword arguments:

            conn = psycopg2.connect(database="test", user="postgres", password="secret")

        Or as a mix of both. The basic connection parameters are:

        :param dsn: Optional[str]
            libpq connection string,
            https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        :param connection_factory:
            Using the *connection_factory* parameter a different class or connections
            factory can be specified. It should be a callable object taking a dsn
            argument.
        :param cursor_factory:
            Using the *cursor_factory* parameter, a new default cursor factory will be
            used by cursor().
        :param dbname: Optional[str]
            The database name
        :param database: Optional[str]
            The database name (only as keyword argument)
        :param user: Optional[str]
            User name used to authenticate
        :param password: Optional[str]
            Password used to authenticate
        :param host: Optional[str]
            Database host address (defaults to UNIX socket if not provided)
        :param port: Optional[int]
            Connection port number (defaults to 5432 if not provided)
        :param \**kwargs:
            Any other keyword parameter will be passed to the underlying client
            library: the list of supported parameters depends on the library version.
            See bellow

        :Keyword Arguments:
            * *async* (boolean) --
                Using *async*=True an asynchronous connection will be created. *async_* is
                a valid alias (for Python versions where ``async`` is a keyword).
        """
        super().__init__(_log)

        self._dsn = dsn
        self._connection_factory = connection_factory
        self._cursor_factory = cursor_factory
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._kwargs = kwargs

        dsn_message_optional = ""
        if self._dsn:
            dsn_message_optional = f"dsn: {dsn}, "
        _log.debug(
            f"Creating new PostgreSQL connection for {dsn_message_optional}"
            f"user: {user} to [host:port/dbname]: {host}:{port}/{dbname}"
        )

    def _connect(self):
        import psycopg2

        return psycopg2.connect(
            dsn=self._dsn,
            connection_factory=self._connection_factory,
            cursor_factory=self._cursor_factory,
            dbname=self._dbname,
            user=self._user,
            password=self._password,
            host=self._host,
            port=self._port,
            **self._kwargs,
        )

    def execute_query(self, query: str) -> List[List[Any]]:
        try:
            return super().execute_query(query)
        finally:
            self.commit()
