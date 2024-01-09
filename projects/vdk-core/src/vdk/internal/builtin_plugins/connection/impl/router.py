# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Callable
from typing import Dict
from typing import Union

from vdk.api.plugin.plugin_input import IManagedConnectionRegistry
from vdk.internal.builtin_plugins.config.vdk_config import DB_DEFAULT_TYPE
from vdk.internal.builtin_plugins.connection.connection_hooks import (
    ConnectionHookSpecFactory,
)
from vdk.internal.builtin_plugins.connection.impl.wrapped_connection import (
    WrappedConnection,
)
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from vdk.internal.core import errors
from vdk.internal.core.config import Configuration

log = logging.getLogger(__name__)


class ManagedConnectionRouter(IManagedConnectionRegistry):
    """
    Create ManagedConnection by routing the configured database plugin.
    Configuration is controlled by DB_DEFAULT_TYPE for default connection.
    Or specific connection can be specified by open_connection(dbtype)
    In both cases dbtype must match the string in which the plugin register itself with.
    """

    def __init__(
        self,
        cfg: Configuration,
        connection_hook_spec_factory: ConnectionHookSpecFactory,
    ):
        self._cfg: Configuration = cfg
        self._connection_hook_spec_factory = connection_hook_spec_factory
        self._log: logging.Logger = logging.getLogger(__name__)
        self._connections: Dict[str, ManagedConnectionBase] = dict()
        self._connection_builders: Dict[
            str, Callable[[], ManagedConnectionBase]
        ] = dict()

    def add_open_connection_factory_method(
        self,
        dbtype: str,
        open_connection_func: Callable[
            [], Union[ManagedConnectionBase, PEP249Connection]
        ],
    ) -> None:
        """
        Add new connection factory method. See parent doc for more.
        """
        self._connection_builders[dbtype.lower()] = open_connection_func

    def open_default_connection(self) -> ManagedConnectionBase:
        """
        Open connection to the database configured as default (by db_default_type option).
        """
        dbtype = self._cfg.get_value(DB_DEFAULT_TYPE)
        if dbtype is None:
            if len(self._connection_builders) == 1:
                dbtype = list(self._connection_builders.keys())[0]
                self._log.debug(
                    f"DB_DEFAULT_TYPE has not been set. Found one database supported: {dbtype}. Will use it as default"
                )

        return self.open_connection(dbtype)

    def open_connection(self, dbtype: str) -> ManagedConnectionBase:
        """
        Opens a connection for the given database type.

        :param dbtype: The type of connection to open. It needs to have been registered before that by add_connection_builder
        or it will thrown an error
        :return: the new connection if successful or throws an exception
        """
        dbtype = dbtype.lower() if dbtype else None
        conn = None
        if dbtype in self._connections:
            conn = self._connections[dbtype]
        elif dbtype in self._connection_builders:
            self._log.debug(f"Connection to {dbtype} is missing. Will try to connect")
            conn = self.__create_connection(dbtype)
        else:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"Provided configuration variable for {DB_DEFAULT_TYPE} has invalid value.",
                    f"VDK was run with {DB_DEFAULT_TYPE}={dbtype}, however {dbtype} is invalid value for this variable.",
                    f"Provide either valid value for {DB_DEFAULT_TYPE} or install database plugin that supports this type. "
                    f"Currently possible values are {list(self._connection_builders.keys())}",
                )
            )
        if not conn._is_connected():
            conn.connect()
        return conn

    def __cache_connection(self, dbType: str, conn: ManagedConnectionBase):
        if dbType in self._connections:
            # Though not expected, this checks is added to reduce the chance of connection leaks.
            log.warning(
                f"There is already cached connection for dbType {dbType}. Replacing it "
            )
            prev_conn = self._connections[dbType]
            try:
                prev_conn.close()
            except Exception as e:
                log.debug(
                    f"Failed to close cached connection: {e}. Likely it's no longer valid."
                )
        self._connections[dbType] = conn

    def __create_connection(self, dbtype: str):
        conn = self._connection_builders[dbtype]()
        if isinstance(conn, ManagedConnectionBase):
            self.__cache_connection(dbtype, conn)
            if not conn._connection_hook_spec_factory:
                conn._connection_hook_spec_factory = self._connection_hook_spec_factory
        elif conn is None:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"Could not create new connection of db type {dbtype}.",
                    f"VDK was run with {DB_DEFAULT_TYPE}={dbtype}, however no valid connection was created.",
                    f"Seems to be a bug in the plugin for dbtype {dbtype}. Make sure it's correctly installed. "
                    f"If upgraded recently consider reverting to previous version. Or use another db type. "
                    f"Currently possible values are {list(self._connection_builders.keys())}",
                )
            )
        else:
            log = logging.getLogger(conn.__class__.__name__)
            # we will let ManagedConnection to open it when needed.
            conn.close()
            wrapped_conn = WrappedConnection(
                log,
                self._connection_builders[dbtype],
                self._connection_hook_spec_factory,
            )
            self.__cache_connection(dbtype, wrapped_conn)

        return self._connections[dbtype]
