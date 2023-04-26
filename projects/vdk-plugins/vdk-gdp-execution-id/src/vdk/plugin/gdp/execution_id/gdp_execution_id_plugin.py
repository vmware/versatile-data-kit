# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.gdp.execution_id.gdp_execution_id_configuration import add_definitions
from vdk.plugin.gdp.execution_id.gdp_execution_id_configuration import (
    GdpExecutionIdPluginConfiguration,
)

GDP_EXECUTION_ID_MICRO_DIMENSION_NAME = "GDP_EXECUTION_ID_MICRO_DIMENSION_NAME"

log = logging.getLogger(__name__)


class GdpExecutionIdPlugin(IIngesterPlugin):
    def __init__(self):
        self._plugin_config = None
        self.__execution_id = None

    def pre_ingest_process(
        self,
        payload: List[dict],
        destination_table: Optional[str] = None,
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
        metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> Tuple[List[Dict], Optional[IIngesterPlugin.IngestionMetadata]]:
        for p in payload:
            p.update({self._plugin_config.micro_dimension_name(): self.__execution_id})
        return payload, metadata

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with GDP Execution ID Plugin.")
        self._plugin_config = GdpExecutionIdPluginConfiguration(
            context.core_context.configuration
        )
        self.__execution_id = context.core_context.state.get(
            CommonStoreKeys.EXECUTION_ID
        )
        context.ingester.add_ingester_factory_method(
            "vdk-gdp-execution-id", lambda: self
        )

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder) -> None:
        add_definitions(config_builder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(
        GdpExecutionIdPlugin(), "gdp-execution-id-plugin"
    )
