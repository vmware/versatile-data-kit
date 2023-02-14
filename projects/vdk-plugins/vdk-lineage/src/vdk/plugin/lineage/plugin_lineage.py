# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import uuid
from abc import abstractmethod
from typing import List
from typing import Optional

from openlineage.client import OpenLineageClient
from openlineage.client.facet import ParentRunFacet
from openlineage.client.run import RunEvent
from openlineage.client.run import RunState
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_state import ExecutionStateStoreKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.internal.core.statestore import StoreKey
from vdk.internal.plugin.plugin import PluginRegistry
from vdk.plugin.lineage import openlineage_config
from vdk.plugin.lineage.openlineage_config import OpenLineageConfiguration
from vdk.plugin.lineage.openlineage_utils import run_event
from vdk.plugin.lineage.openlineage_utils import setup_client
from vdk.plugin.lineage.openlineage_utils import sql_event
from vdk.plugin.lineage.openlineage_utils import VdkJobFacet

log = logging.getLogger(__name__)


class IOpenLineageClient:
    @abstractmethod
    def emit(self, event: RunEvent):
        pass


OPENLINEAGE_LOGGER_KEY = StoreKey[IOpenLineageClient]("open-lineage-logger")


class OpenLineagePlugin:
    def __init__(self):
        self.__client: Optional[OpenLineageClient] = None
        self.__op_id = None
        self.__execution_id = None
        self.__job_version = None
        self.__team = None
        self.__job_name = None
        self.__namespace = "versatile_data_kit"
        self.__job_run_id = str(uuid.uuid4())

    @hookimpl
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        """
        Here we define what configuration settings are needed for openlineage.
        """
        openlineage_config.add_definitions(config_builder)

    @hookimpl
    def vdk_initialize(self, context: CoreContext):
        config = OpenLineageConfiguration(context.configuration)
        if config.url():
            log.debug(f"Open lineage client is enabled at url: {config.url()}")
            self.__client = setup_client(config.url(), config.api_key())
        elif context.state.get(OPENLINEAGE_LOGGER_KEY) is not None:
            self.__client = context.state.get(OPENLINEAGE_LOGGER_KEY)
            log.debug(
                f"Open lineage client custom implementation set. Type: {type(self.__client)} "
            )
        else:
            log.debug(
                "No OpenLineage url set. Collecting openlineage data is disabled."
            )

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        if self.__client:
            self.__execution_id = context.core_context.state.get(
                CommonStoreKeys.EXECUTION_ID
            )
            self.__op_id = context.core_context.state.get(CommonStoreKeys.OP_ID)
            self.__job_version = context.core_context.state.get(
                ExecutionStateStoreKeys.JOB_GIT_HASH
            )
            self.__team = context.core_context.configuration.get_value(
                JobConfigKeys.TEAM
            )
            self.__job_name = context.job_input.get_name()

            self.__emit_run_event(RunState.START)

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        out: HookCallResult
        out = yield
        if self.__client:
            result: ExecutionResult = out.get_result()
            self.__execution_id = context.core_context.state.get(
                CommonStoreKeys.EXECUTION_ID
            )
            self.__op_id = context.core_context.state.get(CommonStoreKeys.OP_ID)
            self.__emit_run_event(
                RunState.COMPLETE if result.is_success() else RunState.FAIL
            )
        return None

    @hookimpl(trylast=True)
    def db_connection_decorate_operation(self, decoration_cursor: DecorationCursor):
        if self.__client:
            # TODO: track properly the run state (start and end of the query)
            # For now it's always complete since we have not easy way to know start/end.
            # TODO: find a way to extract the database connection type (impala vs trino)
            #  and the actual connection (e.g connection URI - be impala-1.foo.com impala-2.foo.com)
            # and record them either as facet or OpenLinage Source
            query = decoration_cursor.get_managed_operation().get_operation()
            try:
                #  TODO: abstract away so there could be multiple lineage loggers (nit just openlineage)
                self.__client.emit(
                    sql_event(
                        RunState.OTHER,
                        query,
                        self.__namespace,
                        self.__job_run_id,
                        ParentRunFacet.create(
                            self.__job_run_id, self.__namespace, self.__job_name
                        ),
                    )
                )
            except Exception as e:
                log.exception(
                    f"Failed to send lineage data for query {query}. Will continue without it. Errors was {e}"
                )
                raise e

    def __emit_run_event(self, state: RunState):
        try:
            run_details = VdkJobFacet(
                self.__op_id, self.__execution_id, self.__job_version, self.__team
            )
            self.__client.emit(
                run_event(
                    state,
                    self.__job_name,
                    self.__namespace,
                    self.__job_run_id,
                    None,
                    run_details,
                )
            )
        except Exception as e:
            log.exception(
                f"Failed to send lineage data for the job. Will continue without it. Errors was {e}."
            )


@hookimpl
def vdk_start(plugin_registry: PluginRegistry, command_line_args: List) -> None:
    """
    Load all lineage vdk plugins
    """
    plugin_registry.load_plugin_with_hooks_impl(OpenLineagePlugin())
