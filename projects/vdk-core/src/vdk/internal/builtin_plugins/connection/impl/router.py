# Copyright 2021 VMware, Inc.
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


class ManagedConnectionRouter(IManagedConnectionRegistry):
    """
    Create ManagedConnection by routing the configured database plugin.
    Configuration is controlled by DB_DEFAULT_TYPE for defualt connection.
    Or specfific connection can be specified by open_connection(dbtype)
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
        self._connection_builders[dbtype] = open_connection_func

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
        :param dbtype: The type of connection to open. It needs to have been registered before that by add_connection_builder
        or it will thrown an error
        :return: the new connection if succesfull or throws an expception
        """
        if dbtype in self._connections:
            conn = self._connections[dbtype]
            if conn._is_connected():
                return conn
            else:
                conn._connect()
                return conn
        self._log.debug(f"Connection to {dbtype} is missing. Will try to connect")
        if dbtype in self._connection_builders:
            return self.__create_connection(dbtype)
        errors.log_and_throw(
            to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
            log=self._log,
            what_happened=f"Provided configuration variable for {DB_DEFAULT_TYPE} has invalid value.",
            why_it_happened=f"VDK was run with {DB_DEFAULT_TYPE}={dbtype}, however {dbtype} is invalid value for this variable.",
            consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
            countermeasures=f"Provide either valid value for {DB_DEFAULT_TYPE} or install database plugin that supports this type. "
            f"Currently possible values are {list(self._connection_builders.keys())}",
        )

    def __create_connection(self, dbtype):
        conn = self._connection_builders[dbtype]()
        if isinstance(conn, ManagedConnectionBase):
            self._connections[dbtype] = conn
            if not conn._connection_hook_spec_factory:
                conn._connection_hook_spec_factory = self._connection_hook_spec_factory
        elif conn is None:
            errors.log_and_throw(
                to_be_fixed_by=errors.ResolvableBy.CONFIG_ERROR,
                log=self._log,
                what_happened=f"Could not create new connection of db type {dbtype}.",
                why_it_happened=f"VDK was run with {DB_DEFAULT_TYPE}={dbtype}, however no valid connection was created.",
                consequences=errors.MSG_CONSEQUENCE_DELEGATING_TO_CALLER__LIKELY_EXECUTION_FAILURE,
                countermeasures=f"Seems to be a bug in the plugin for dbtype {dbtype}. Make sure it's correctly installed. "
                f"If upgraded recently consider reverting to previous version. Or use another db type. "
                f"Currently possible values are {list(self._connection_builders.keys())}",
            )
        else:
            log = logging.getLogger(conn.__class__.__name__)
            conn.close()  # we will let ManagedConnection to open it when needed.
            self._connections[dbtype] = WrappedConnection(
                log,
                self._connection_builders[dbtype],
                self._connection_hook_spec_factory,
            )
        return self._connections[dbtype]
