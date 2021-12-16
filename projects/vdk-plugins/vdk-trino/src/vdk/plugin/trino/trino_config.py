# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

from vdk.internal.core.config import Configuration

TRINO_HOST = "TRINO_HOST"
TRINO_PORT = "TRINO_PORT"
TRINO_SCHEMA = "TRINO_SCHEMA"
TRINO_CATALOG = "TRINO_CATALOG"
TRINO_USER = "TRINO_USER"
TRINO_PASSWORD = "TRINO_PASSWORD"
TRINO_USE_SSL = "TRINO_USE_SSL"
TRINO_SSL_VERIFY = "TRINO_SSL_VERIFY"
TRINO_TIMEOUT_SECONDS = "TRINO_TIMEOUT_SECONDS"
TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY = "TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY"

trino_templates_data_to_target_strategy: str = ""


class TrinoConfiguration:
    def __init__(self, config: Configuration) -> None:
        self.__config = config

    def host(self) -> str:
        return cast(str, self.__config.get_required_value(TRINO_HOST))

    def port(self) -> int:
        return cast(int, self.__config.get_required_value(TRINO_PORT))

    def schema(self) -> str:
        return cast(str, self.__config.get_value(TRINO_SCHEMA))

    def catalog(self) -> str:
        return cast(str, self.__config.get_value(TRINO_CATALOG))

    def user(self) -> str:
        return cast(str, self.__config.get_required_value(TRINO_USER))

    def password(self) -> str:
        return cast(str, self.__config.get_value(TRINO_PASSWORD))

    def use_ssl(self) -> bool:
        return cast(bool, self.__config.get_value(TRINO_USE_SSL))

    def ssl_verify(self) -> bool:
        return cast(bool, self.__config.get_value(TRINO_SSL_VERIFY))

    def timeout_seconds(self) -> int:
        return cast(int, self.__config.get_value(TRINO_TIMEOUT_SECONDS))

    def templates_data_to_target_strategy(self) -> str:
        return cast(
            str, self.__config.get_value(TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY)
        )


def add_definitions(config_builder):
    """
    Here we define what configuration settings are needed for trino with reasonable defaults
    """
    config_builder.add(
        key=TRINO_HOST,
        default_value="localhost",
        description="The host we need to connect.",
    )
    config_builder.add(
        key=TRINO_PORT, default_value=28080, description="The port to connect to"
    )
    config_builder.add(
        key=TRINO_USE_SSL,
        default_value=True,
        description="Set if database connection uses SSL",
    )
    config_builder.add(
        key=TRINO_SSL_VERIFY,
        default_value=True,
        description="Verify the SSL certificate",
    )
    config_builder.add(
        key=TRINO_SCHEMA, default_value="default", description="The database schema"
    )
    config_builder.add(
        key=TRINO_CATALOG, default_value="memory", description="The database catalog"
    )
    config_builder.add(key=TRINO_USER, default_value="unknown", description="User name")
    config_builder.add(
        key=TRINO_PASSWORD, default_value=None, description="User password"
    )
    config_builder.add(
        key=TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY,
        default_value="INSERT_SELECT",
        description="What strategy is used when moving data from source table to target table in templates."
        "Possible values are:\n"
        "INSERT_SELECT - target is created, data from source is inserted into target, source is dropped;\n"
        "RENAME - source is renamed to target;\n",
    )
    config_builder.add(
        key=TRINO_TIMEOUT_SECONDS,
        default_value=None,
        description="The trino query timeout in seconds.",
    )
