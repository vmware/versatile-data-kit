# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib
import tempfile
from typing import Dict
from typing import Optional

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

ORACLE_USER = "ORACLE_USER"
ORACLE_PASSWORD = "ORACLE_PASSWORD"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"


class OracleConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_oracle_user(self) -> str:
        return self.__config.get_value(ORACLE_USER)

    def get_oracle_password(self) -> str:
        return self.__config.get_value(ORACLE_PASSWORD)

    def get_oracle_connection_string(self) -> Optional[Dict[str, str]]:
        return self.__config.get_value(ORACLE_CONNECTION_STRING)

    @staticmethod
    def add_definitions(config_builder: ConfigurationBuilder):
        config_builder.add(
            key=ORACLE_USER,
            default_value=None,
            is_sensitive=True,
            description="The Oracle user for the database connection",
        )
        config_builder.add(
            key=ORACLE_PASSWORD,
            default_value=None,
            is_sensitive=True,
            description="The oracle password for the database connection",
        )
        config_builder.add(
            key=ORACLE_CONNECTION_STRING,
            default_value=None,
            is_sensitive=True,
            description="The Oracle database connection string",
        )
