# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.utils import parse_config_sequence

SQL_EXTENSIONS_SPLIT_QUERIES_ENABLED = "SQL_EXTENSIONS_SPLIT_QUERIES_ENABLED"


class SqlExtensionsConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_properties_default_type(self) -> bool:
        return bool(self.__config.get_value(SQL_EXTENSIONS_SPLIT_QUERIES_ENABLED))


@hookimpl
def vdk_configure(config_builder: ConfigurationBuilder):
    add_definitions(config_builder)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=SQL_EXTENSIONS_SPLIT_QUERIES_ENABLED,
        default_value=False,
        description="If set to true it will split queries using ';' delimiter.",
    )
