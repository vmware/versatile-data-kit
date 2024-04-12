# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib
import tempfile

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

SQLITE_MULTIPLE_DB = "SQLITE_MULTIPLE_DB"
SQLITE_FILE = "SQLITE_FILE"
SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED = "SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED"


class SQLiteConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_auto_create_table_enabled(self) -> bool:
        return self.__config.get_value(SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED)

    def get_sqlite_file(self) -> pathlib.Path:
        return pathlib.Path(self.__config.get_value(SQLITE_FILE))

    def get_sqlite_multiple_db(self) -> bool:
        return self.__config.get_value(SQLITE_MULTIPLE_DB)


def add_default_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=SQLITE_MULTIPLE_DB,
        default_value="",
        is_sensitive=False,
        description="Add names of the SQLite Databases you want to register."
                    "Example: SQLITE_MULTIPLE_DB=prod_db,test_db"
                    "If you use multiple databases you need to use all the SQLite config options with db name "
                    "prefix: "
                    "<db_name>_SQLITE_FILE, (example: PROD_DB_SQLITE_FILE and TEST_DB_SQLITE_FILE) ",
    )
    config_builder.add(
        key=SQLITE_FILE,
        default_value=str(
            pathlib.Path(tempfile.gettempdir()).joinpath("vdk-sqlite.db")
        ),
        description="The file of the sqlite database.",
    )
    config_builder.add(
        key=SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED,
        default_value=True,
        description="If set to true, auto create table if it does not exists during ingestion."
        "This is only applicable when ingesting data into sqlite (ingest method is sqlite).",
    )


