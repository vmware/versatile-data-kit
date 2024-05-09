# Copyright 2023-2024 Broadcom
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
ORACLE_THICK_MODE_LIB_DIR = "ORACLE_THICK_MODE_LIB_DIR"
ORACLE_CONNECTION_STRING = "ORACLE_CONNECTION_STRING"
ORACLE_HOST = "ORACLE_HOST"
ORACLE_PORT = "ORACLE_PORT"
ORACLE_SID = "ORACLE_SID"
ORACLE_SERVICE_NAME = "ORACLE_SERVICE_NAME"
ORACLE_INGEST_BATCH_SIZE = "ORACLE_INGEST_BATCH_SIZE"


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


class OracleConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_oracle_user(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_USER, section=section)

    def get_oracle_password(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_PASSWORD, section=section)

    def get_oracle_connection_string(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_CONNECTION_STRING, section=section)

    def get_oracle_host(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_HOST, section=section)

    def get_oracle_port(self, section: Optional[str]) -> int:
        return int(self.__config.get_value(key=ORACLE_PORT, section=section))

    def get_oracle_sid(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_SID, section=section)

    def get_oracle_service_name(self, section: Optional[str]) -> str:
        return self.__config.get_value(key=ORACLE_SERVICE_NAME, section=section)

    def oracle_use_secrets(self, section: Optional[str]) -> bool:
        return self.__config.get_value(key=ORACLE_USE_SECRETS, section=section)

    def oracle_thick_mode(self, section: Optional[str]) -> bool:
        return parse_boolean(
            self.__config.get_value(key=ORACLE_THICK_MODE, section=section)
        )

    def oracle_thick_mode_lib_dir(self, section: Optional[str]) -> Optional[str]:
        return self.__config.get_value(key=ORACLE_THICK_MODE_LIB_DIR, section=section)

    def oracle_ingest_batch_size(self, section: Optional[str]) -> Optional[int]:
        if self.__config.get_value(key=ORACLE_INGEST_BATCH_SIZE, section=section):
            return int(
                self.__config.get_value(key=ORACLE_INGEST_BATCH_SIZE, section=section)
            )
        else:
            return 100

    @staticmethod
    def add_default_definition(config_builder: ConfigurationBuilder):
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
            key=ORACLE_HOST,
            default_value=None,
            is_sensitive=True,
            description="The host of the Oracle database. Note: This option is overridden by ORACLE_CONNECTION_STRING ",
        )
        config_builder.add(
            key=ORACLE_PORT,
            default_value=1521,
            is_sensitive=True,
            description="The port of the Oracle database. Note: This option is overridden by ORACLE_CONNECTION_STRING",
        )
        config_builder.add(
            key=ORACLE_SID,
            default_value=None,
            is_sensitive=True,
            description="The schema id of the Oracle database. Note: This option is overridden by ORACLE_CONNECTION_STRING",
        )
        config_builder.add(
            key=ORACLE_SERVICE_NAME,
            default_value=None,
            is_sensitive=True,
            description="The service name of the Oracle database. Note: This option is overridden by ORACLE_CONNECTION_STRING",
        )
        config_builder.add(
            key=ORACLE_USE_SECRETS,
            default_value=True,
            description="Set this flag to use secrets to connect to Oracle. This is protype option. "
            "Leave default value unless there are issues.",
        )
        config_builder.add(
            key=ORACLE_THICK_MODE,
            default_value=True,
            description="Use oracle thick mode. Set to False to disable oracle thick mode."
            "If set to true you may need to manually install client library. "
            "Refer to "
            "https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#enablingthick "
            "More info: https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_b.html",
        )
        config_builder.add(
            key=ORACLE_THICK_MODE_LIB_DIR,
            default_value=None,
            description="This is the location of the Oracle Client library used when thick mode is enabled. "
            "This option is ignored if ORACLE_THICK_MODE is false."
            "Before setting this follow instruction in "
            "https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#enablingthick ",
        )
        config_builder.add(
            key=ORACLE_INGEST_BATCH_SIZE,
            default_value=100,
            description="Batch size when ingesting records into Oracle.",
        )
