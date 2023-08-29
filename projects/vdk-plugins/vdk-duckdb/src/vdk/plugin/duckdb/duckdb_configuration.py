# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib
import tempfile

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

DUCKDB_FILE = "DUCKDB_FILE"
DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED = "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED"


class DuckDBConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_auto_create_table_enabled(self) -> bool:
        return self.__config.get_value(DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED)

    def get_duckdb_file(self):
        duckdb_file_path = self.__config.get_value(DUCKDB_FILE) or "default_path.duckdb"
        return pathlib.Path(duckdb_file_path)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=DUCKDB_FILE,
        default_value=str(
            pathlib.Path(tempfile.gettempdir()).joinpath("vdk-duckdb.db")
        ),
        description="The file of the DuckDB database.",
    )
    config_builder.add(
        key=DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED,
        default_value=True,
        description="If set to true, auto create table if it does not exist during ingestion."
        "This is only applicable when ingesting data into DuckDB (ingest method is DuckDB).",
    )
