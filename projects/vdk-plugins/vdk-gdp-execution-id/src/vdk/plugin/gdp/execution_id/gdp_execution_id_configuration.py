# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

GDP_EXECUTION_ID_MICRO_DIMENSION_NAME = "GDP_EXECUTION_ID_MICRO_DIMENSION_NAME"


class GdpExecutionIdPluginConfiguration:
    def __init__(self, configuration: Configuration):
        self.__core_config = configuration

    def micro_dimension_name(self):
        return self.__core_config.get_value(GDP_EXECUTION_ID_MICRO_DIMENSION_NAME)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=GDP_EXECUTION_ID_MICRO_DIMENSION_NAME,
        default_value="vdk_gdp_execution_id",
        description="The name of the micro-dimension that is added to each payload sent for ingestion.",
    )
