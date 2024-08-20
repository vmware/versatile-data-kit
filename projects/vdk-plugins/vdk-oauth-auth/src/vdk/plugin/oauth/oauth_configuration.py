# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder


CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"


class OauthPluginConfiguration:
    def __init__(
        self,
        config: Configuration,
    ):
        self.__config = config

    def client_id(self):
        return self.__config.get_value(CLIENT_ID)

    def client_secret(self):
        return self.__config.get_value(CLIENT_SECRET)


def add_definitions(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key=CLIENT_ID,
        default_value=None,
        description="client id for oauth authentication",
    )
    config_builder.add(
        key=CLIENT_SECRET,
        default_value=None,
        description="client secret for oauth authentication",
    )
