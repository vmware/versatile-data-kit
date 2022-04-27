# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import textwrap
from typing import List
from typing import Optional

from vdk.api.job_input import IJobArguments
from vdk.api.job_input import IJobInput
from vdk.api.job_input import ITemplate
from vdk.internal.builtin_plugins.connection.impl.router import ManagedConnectionRouter
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from vdk.internal.builtin_plugins.ingestion.ingester_router import IngesterRouter
from vdk.internal.builtin_plugins.job_properties.properties_router import (
    PropertiesRouter,
)
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.sql_argument_substitutor import (
    SqlArgumentSubstitutor,
)
from vdk.internal.core.context import CoreContext
from vdk.internal.core.errors import UserCodeError
from vdk.internal.core.statestore import CommonStoreKeys


# TODO make this extensible so new job inputs can be added by plugins
class JobInput(IJobInput):
    """
    Implementation of JobInput interface.
    It just forwards to actual implementation of a given functionality and should do nothing else.
    """

    def __init__(
        self,
        name: str,
        job_directory: pathlib.Path,
        core_context: CoreContext,
        job_arguments: IJobArguments,
        templates: ITemplate,
        managed_connection_builder: ManagedConnectionRouter,
        ingester: IngesterRouter,
        properties_router: PropertiesRouter,
    ):
        """Constructor."""

        self.__name = name
        self.__job_directory = job_directory
        self.__statestore = core_context.state
        self.__job_arguments = job_arguments
        self.__templates = templates
        self.__managed_connection_builder = managed_connection_builder
        self.__ingester = ingester
        self.__properties_router = properties_router
        self.__vdk_internal_telemetry = None

    # Connections

    def get_managed_connection(self) -> ManagedConnectionBase:
        return self.__managed_connection_builder.open_default_connection()

    def get_arguments(self) -> dict:
        return self.__job_arguments.get_arguments()

    # Properties

    def get_property(self, name, default_value=None):
        return self.__properties_router.get_property(name, default_value)

    def get_all_properties(self):
        return self.__properties_router.get_all_properties()

    def set_all_properties(self, properties):
        return self.__properties_router.set_all_properties(properties)

    def _substitute_query_params(self, sql: str):
        sql = textwrap.dedent(sql).strip("\n") + "\n"
        query = sql
        sql_susbstitute_args = {}
        if not self.__properties_router.has_properties_impl():
            logging.getLogger(__name__).info(
                "Data Job Properties has not been initialized., "
                "so I won't be able to provide query properties substitution capabilities from job properties."
                "If passed job arguments will still be used"
            )
        else:
            sql_susbstitute_args.update(self.get_all_properties())
        sql_susbstitute_args.update(self.get_execution_properties())

        sql_args = self.get_arguments()
        if not sql_args or type(sql_args) != dict:
            logging.getLogger(__name__).debug(
                "No arguments are passed for Data Job, "
                "so I won't be able to provide query parameter substitution capabilities with job arguments."
            )
        else:
            sql_susbstitute_args.update(sql_args)
        query = SqlArgumentSubstitutor(sql_susbstitute_args).substitute(query)

        return query

    def execute_query(self, sql: str):
        if not sql or not sql.strip():
            raise UserCodeError("Trying to execute an empty SQL query.")

        query = self._substitute_query_params(sql)

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
            result = self.__templates.execute_template(template_name, template_args)

            return result
        else:
            raise NotImplemented("Templates not wired to JobInput")

    def get_name(self) -> str:
        return self.__name

    def get_job_directory(self) -> pathlib.Path:
        return self.__job_directory

    def get_execution_properties(self) -> dict:
        start_time = self.__statestore.get(CommonStoreKeys.START_TIME)
        return {
            "pa__execution_id": self.__statestore.get(CommonStoreKeys.EXECUTION_ID),
            "pa__job_start_unixtime": str(int(start_time.timestamp())),
            "pa__job_start_ts_expr": f"cast ({start_time.timestamp()} as timestamp)",
            "pa__op_id": self.__statestore.get(CommonStoreKeys.OP_ID),
        }
