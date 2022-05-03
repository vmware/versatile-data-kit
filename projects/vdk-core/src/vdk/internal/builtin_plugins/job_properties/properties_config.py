# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.util.utils import parse_config_sequence

PROPERTIES_DEFAULT_TYPE = "PROPERTIES_DEFAULT_TYPE"
PROPERTIES_WRITE_PREPROCESS_SEQUENCE = "PROPERTIES_WRITE_PREPROCESS_SEQUENCE"


class PropertiesConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def get_properties_default_type(self) -> str:
        return self.__config.get_value(PROPERTIES_DEFAULT_TYPE)

    def get_properties_write_preprocess_sequence(self) -> List[str]:
        return parse_config_sequence(
            self.__config, key=PROPERTIES_WRITE_PREPROCESS_SEQUENCE, sep=","
        )


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
    config_builder.add(
        key="PROPERTIES_WRITE_PREPROCESS_SEQUENCE",
        default_value=None,
        description="""A string of comma-separated property types.
            Those types are priorly registered in the IPropertiesRegistry, by
            mapping a factory for instantiating each IPropertiesServiceClient
            property type handler.
            This comma-separated string value indicates the sequence in which those
            IPropertiesServiceClient implementations `write_properties` method
            will be invoked. For example:
                   PROPERTIES_WRITE_PREPROCESS_SEQUENCE="a-prefixed-property,
                   replicated-property"
            would mean that the properties data stored would be first
            processed by the `a-prefixed-property` client, then by the
            `replicated-property` client, and finally would be stored by
            the default properties client.
            In case of pre-processing failure, the default client won't be invoked.
            """,
    )
