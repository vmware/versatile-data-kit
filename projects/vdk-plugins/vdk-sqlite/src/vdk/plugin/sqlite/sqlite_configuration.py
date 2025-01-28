# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib
import tempfile

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

SQLITE_FILE = "SQLITE_FILE"
SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED = "SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED"


class SQLiteConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_auto_create_table_enabled(self, section: str = "vdk") -> bool:
        return self.__config.get_value(
            SQLITE_INGEST_AUTO_CREATE_TABLE_ENABLED, section=section
        )

    def get_sqlite_file(self, section: str = "vdk") -> pathlib.Path:
        path = self.__config.get_value(SQLITE_FILE, section=section)
        return pathlib.Path(path)


def add_definitions(config_builder: ConfigurationBuilder):
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
