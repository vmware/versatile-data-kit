# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from typing import cast
from typing import Optional

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


def parse_boolean(value):
    true_values = ["true", "1", "yes", "on"]
    false_values = ["false", "0", "no", "off"]

    str_value = str(value).strip().lower()

    if str_value in true_values:
        return True
    elif str_value in false_values:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")


class TrinoConfiguration:
    def __init__(self, config: Configuration) -> None:
        self.__config = config

    def host(self, section: Optional[str]) -> str:
        return cast(
            str, self.__config.get_required_value(key=TRINO_HOST, section=section)
        )

    def port(self, section: Optional[str]) -> int:
        return cast(
            int, self.__config.get_required_value(key=TRINO_PORT, section=section)
        )

    def schema(self, section: Optional[str]) -> str:
        return (
            cast(str, self.__config.get_value(key=TRINO_SCHEMA, section=section))
            if self.__config.get_value(key=TRINO_SCHEMA, section=section) is not None
            else "default"
        )

    def catalog(self, section: Optional[str]) -> str:
        return (
            cast(str, self.__config.get_value(key=TRINO_CATALOG, section=section))
            if self.__config.get_value(key=TRINO_CATALOG, section=section) is not None
            else "memory"
        )

    def user(self, section: Optional[str]) -> str:
        return (
            cast(str, self.__config.get_required_value(key=TRINO_USER, section=section))
            if self.__config.get_value(key=TRINO_USER, section=section) is not None
            else "unknown"
        )

    def password(self, section: Optional[str]) -> str:
        return (
            cast(str, self.__config.get_value(key=TRINO_PASSWORD, section=section))
            if self.__config.get_value(key=TRINO_PASSWORD, section=section) is not None
            else None
        )

    def use_ssl(self, section: Optional[str]) -> bool:
        return (
            parse_boolean(self.__config.get_value(key=TRINO_USE_SSL, section=section))
            if (self.__config.get_value(key=TRINO_USE_SSL, section=section) is not None)
            else True
        )

    def ssl_verify(self, section: Optional[str]) -> bool:
        return (
            parse_boolean(
                self.__config.get_value(key=TRINO_SSL_VERIFY, section=section)
            )
            if (
                self.__config.get_value(key=TRINO_SSL_VERIFY, section=section)
                is not None
            )
            else True
        )

    def timeout_seconds(self, section: Optional[str]) -> int:
        return (
            cast(
                int, self.__config.get_value(key=TRINO_TIMEOUT_SECONDS, section=section)
            )
            if (
                self.__config.get_value(key=TRINO_TIMEOUT_SECONDS, section=section)
                is not None
            )
            else None
        )

    def templates_data_to_target_strategy(self, section: Optional[str]) -> str:
        return cast(
            str,
            self.__config.get_value(
                key=TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY, section=section
            )
            if (
                self.__config.get_value(
                    key=TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY, section=section
                )
                is not None
            )
            else "INSERT_SELECT",
        )

    @staticmethod
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
            key=TRINO_CATALOG,
            default_value="memory",
            description="The database catalog",
        )
        config_builder.add(
            key=TRINO_USER, default_value="unknown", description="User name"
        )
        config_builder.add(
            key=TRINO_PASSWORD, default_value=None, description="User password"
        )
        config_builder.add(
            key=TRINO_TEMPLATES_DATA_TO_TARGET_STRATEGY,
            default_value="INSERT_SELECT",
            description="What strategy is used when moving data from source table to target table in templates."
            "Possible values are:\n"
            "INSERT_SELECT - target is created, data from source is inserted into target, source is "
            "dropped;\n"
            "RENAME - source is renamed to target;\n",
        )
        config_builder.add(
            key=TRINO_TIMEOUT_SECONDS,
            default_value=None,
            description="The trino query timeout in seconds.",
        )
