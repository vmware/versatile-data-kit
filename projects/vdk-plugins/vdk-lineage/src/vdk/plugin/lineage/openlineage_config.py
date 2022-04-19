# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

OPENLINEAGE_API_KEY = "OPENLINEAGE_API_KEY"
OPENLINEAGE_URL = "OPENLINEAGE_URL"


class OpenLineageConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def url(self):
        return self.__config.get_value(OPENLINEAGE_URL)

    def api_key(self):
        return self.__config.get_value(OPENLINEAGE_API_KEY)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=OPENLINEAGE_URL,
        default_value=None,
        description="The URL of the service which will consume OpenLineage events.",
    )
    config_builder.add(
        key=OPENLINEAGE_API_KEY,
        default_value=None,
        description="The `Bearer` authentication key used if required by consumer service of OpenLineage events.",
    )
