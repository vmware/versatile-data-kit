# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

SNOWFLAKE_ACCOUNT = "SNOWFLAKE_ACCOUNT"
SNOWFLAKE_USER = "SNOWFLAKE_USER"
SNOWFLAKE_PASSWORD = "SNOWFLAKE_PASSWORD"
SNOWFLAKE_WAREHOUSE = "SNOWFLAKE_WAREHOUSE"
SNOWFLAKE_DATABASE = "SNOWFLAKE_DATABASE"
SNOWFLAKE_SCHEMA = "SNOWFLAKE_SCHEMA"


class SnowflakeConfiguration:
    def __init__(self, config: Configuration) -> None:
        self.__config = config

    def get_snowflake_account(self):
        return self.__config.get_required_value(SNOWFLAKE_ACCOUNT)

    def get_snowflake_user(self):
        return self.__config.get_required_value(SNOWFLAKE_USER)

    def get_snowflake_password(self):
        return self.__config.get_required_value(SNOWFLAKE_PASSWORD)

    def get_snowflake_warehouse(self):
        return self.__config.get_value(SNOWFLAKE_WAREHOUSE)

    def get_snowflake_database(self):
        return self.__config.get_value(SNOWFLAKE_DATABASE)

    def get_snowflake_schema(self):
        return self.__config.get_value(SNOWFLAKE_SCHEMA)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=SNOWFLAKE_ACCOUNT,
        default_value=None,
        description="The Snowflake account identifier as described in https://docs.snowflake.com/en/user-guide/admin-account-identifier.html It is required to connect to a Snowflake instance.",
    )
    config_builder.add(key=SNOWFLAKE_USER, default_value=None, description="User name")
    config_builder.add(
        key=SNOWFLAKE_PASSWORD, default_value=None, description="User password"
    )
    config_builder.add(
        key=SNOWFLAKE_WAREHOUSE,
        default_value=None,
        description="The warehouse to be used.",
    )
    config_builder.add(
        key=SNOWFLAKE_DATABASE,
        default_value=None,
        description="The snowflake database to be used.",
    )
    config_builder.add(
        key=SNOWFLAKE_SCHEMA, default_value=None, description="The database schema"
    )
