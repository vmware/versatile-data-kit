# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.vdk.core.config import Configuration
from taurus.vdk.core.config import ConfigurationBuilder

PROPERTIES_DEFAULT_TYPE = "PROPERTIES_DEFAULT_TYPE"


class PropertiesConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_properties_default_type(self) -> str:
        return self.__config.get_value(PROPERTIES_DEFAULT_TYPE)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=PROPERTIES_DEFAULT_TYPE,
        default_value=None,
        description="Set the default properties type to use. "
        "Plugins can register different properties types. "
        "This option controls which is in use"
        "It can be left empty, in which case "
        "if there is only one type registered it will use it."
        "Or it will use one register with type 'default' ",
    )
