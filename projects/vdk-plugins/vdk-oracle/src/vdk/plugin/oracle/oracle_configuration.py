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
ORACLE_USE_SECRETS = "ORACLE_USE_SECRETS"
ORACLE_THICK_MODE = "ORACLE_THICK_MODE"
ORACLE_USER_SECRET = "ORACLE_USER_SECRET"
ORACLE_PASSWORD_SECRET = "ORACLE_PASSWORD_SECRET"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"


class OracleConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_oracle_user(self) -> str:
        return self.__config.get_value(ORACLE_USER)

    def get_oracle_password(self) -> str:
        return self.__config.get_value(ORACLE_PASSWORD)

    def get_oracle_user_secret(self) -> str:
        return self.__config.get_value(ORACLE_USER_SECRET)

    def get_oracle_password_secret(self) -> str:
        return self.__config.get_value(ORACLE_PASSWORD_SECRET)

    def get_oracle_connection_string(self) -> str:
        return self.__config.get_value(ORACLE_CONNECTION_STRING)

    def oracle_use_secrets(self) -> bool:
        return self.__config.get_value(ORACLE_USE_SECRETS)

    def oracle_thick_mode(self) -> bool:
        return self.__config.get_value(ORACLE_THICK_MODE)

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
            description="The Oracle password for the database connection",
        )
        config_builder.add(
            key=ORACLE_CONNECTION_STRING,
            default_value=None,
            is_sensitive=True,
            description="The Oracle database connection string",
        )
        config_builder.add(
            key=ORACLE_USE_SECRETS,
            default_value=False,
            description="Set this flag to use secrets to connect to Oracle",
        )
        config_builder.add(
            key=ORACLE_USER_SECRET,
            default_value=None,
            description="The user secret key if using secrets to connect to Oracle",
        )
        config_builder.add(
            key=ORACLE_PASSWORD_SECRET,
            default_value=None,
            description="The password secret key if using secrets to connect to Oracle",
        )
        config_builder.add(
            key=ORACLE_THICK_MODE,
            default_value=True,
            description="Use oracle thick mode, default is True. Set to False to disable oracle thick mode. More info: https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_b.html",
        )
