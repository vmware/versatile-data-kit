# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import textwrap
from typing import List
from typing import Optional

from taurus.api.job_input import IJobArguments
from taurus.api.job_input import IJobInput
from taurus.api.job_input import ITemplate
from taurus.vdk.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from taurus.vdk.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from taurus.vdk.builtin_plugins.ingestion.ingester_router import IngesterRouter
from taurus.vdk.builtin_plugins.job_properties.properties_router import PropertiesRouter
from taurus.vdk.builtin_plugins.job_properties.Propertiesnotavailable import (
    PropertiesNotAvailable,
)
from taurus.vdk.builtin_plugins.run.execution_results import ExecutionResult
from taurus.vdk.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from taurus.vdk.builtin_plugins.run.sql_argument_substitutor import (
    SqlArgumentSubstitutor,
)
from taurus.vdk.core.errors import UserCodeError
from taurus.vdk.core.statestore import CommonStoreKeys
from taurus.vdk.core.statestore import StateStore


# TODO make this extensible so new job inputs can be added by plugins
class JobInput(IJobInput):
    """
    Implementation of JobInput interface.
    It just forwards to actual implementation of a given functionality and should do nothing else.
    """

    def __init__(
        self,
        managed_connection_builder: ManagedConnectionRouter,
        statestore: StateStore,
        properties_router: PropertiesRouter,
        job_arguments: IJobArguments,
        templates: ITemplate,
        ingester: IngesterRouter,
    ):
        """Constructor."""

        self.__managed_connection_builder = managed_connection_builder
        self.__statestore = statestore
        self.__properties_router = properties_router
        self.__vdk_internal_telemetry = None
        self.__ingester = ingester
        self.__job_arguments = job_arguments
        self.__templates = templates

    # Connections

    def get_managed_connection(self) -> ManagedConnectionBase:
        return self.__managed_connection_builder.open_default_connection()

    def get_arguments(self) -> dict:
        return self.__job_arguments.get_arguments()

    # Properties

    def get_property(self, name, default_value=None):
        return self.__properties_router.get_properties_impl().get_property(
            name, default_value
        )

    def get_all_properties(self):
        return self.__properties_router.get_properties_impl().get_all_properties()

    def set_all_properties(self, properties):
        return self.__properties_router.get_properties_impl().set_all_properties(
            properties
        )

    def _substitute_query_params(self, sql: str):
        sql = textwrap.dedent(sql).strip("\n") + "\n"
        query = sql
        if isinstance(
            self.__properties_router.get_properties_impl(), PropertiesNotAvailable
        ):
            logging.getLogger(__name__).info(
                "Data Job Properties has not been initialized., "
                "so I won't be able to provide query properties substitution capabilities from job properties."
                "If passed job arguments will still be used"
            )
        else:
            sql_args = self.get_all_properties()
            sql_args.update(self.get_execution_properties())
            query = SqlArgumentSubstitutor(sql_args).substitute(query)

        sql_args = self.get_arguments()
        if not sql_args or type(sql_args) != dict:
            logging.getLogger(__name__).debug(
                "No arguments are passed for Data Job, "
                "so I won't be able to provide query parameter substitution capabilities with job arguments."
            )
        else:
            query = SqlArgumentSubstitutor(sql_args).substitute(query)

        return query

    def execute_query(self, sql: str):
        if not sql or not sql.strip():
            raise UserCodeError("Trying to execute an empty SQL query.")

        job_name = self.__statestore.get(ExecutionStateStoreKeys.JOB_NAME)
        op_id = self.__statestore.get(CommonStoreKeys.OP_ID)

        query = self._substitute_query_params(sql)
        query = "\n".join(
            ["-- job_name: {job_name}", "-- op_id: {op_id}", "{query}"]
        ).format(job_name=job_name, op_id=op_id, query=query)

        connection = self.get_managed_connection()
        return connection.execute_query(query)

    def send_object_for_ingestion(
        self,
        payload: dict,
        destination_table: Optional[str] = None,
        method: Optional[str] = None,
        target: Optional[str] = None,
        collection_id=None,
    ):
        self.__ingester.send_object_for_ingestion(
            payload,
            destination_table,
            method,
            target,
            collection_id,
        )

    def send_tabular_data_for_ingestion(
        self,
        rows: iter,
        column_names: List,
        destination_table: Optional[str] = None,
        method: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        self.__ingester.send_tabular_data_for_ingestion(
            rows,
            column_names,
            destination_table,
            method,
            target,
            collection_id,
        )

    def execute_template(
        self, template_name: str, template_args: dict
    ) -> ExecutionResult:
        if self.__templates:
            return self.__templates.execute_template(template_name, template_args)
        else:
            raise NotImplemented("Templates not wired to JobInput")

    def get_name(self) -> str:
        pass

    def get_job_directory(self) -> pathlib.Path:
        pass

    def get_execution_properties(self) -> dict:
        start_time = self.__statestore.get(CommonStoreKeys.START_TIME)
        return {
            "pa__execution_id": self.__statestore.get(CommonStoreKeys.EXECUTION_ID),
            "pa__job_start_unixtime": str(int(start_time.timestamp())),
            "pa__job_start_ts_expr": f"cast ({start_time.timestamp()} as timestamp)",
            "pa__op_id": self.__statestore.get(CommonStoreKeys.OP_ID),
        }
