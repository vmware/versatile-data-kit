# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib
import tempfile
from typing import Dict
from typing import Optional

from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

DUCKDB_DATABASE = "DUCKDB_DATABASE"
DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED = "DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED"
DUCKDB_CONFIGURATION_DICTIONARY = "DUCKDB_CONFIGURATION_DICTIONARY"


class DuckDBConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_auto_create_table_enabled(self) -> bool:
        return self.__config.get_value(DUCKDB_INGEST_AUTO_CREATE_TABLE_ENABLED)

    def get_duckdb_database(self):
        return self.__config.get_value(DUCKDB_DATABASE) or "default_path.duckdb"

    def get_duckdb_configuration_dictionary(self) -> Optional[Dict[str, str]]:
        config_dict_str = self.__config.get_value(DUCKDB_CONFIGURATION_DICTIONARY)
        if config_dict_str:
            return json.loads(config_dict_str)
        else:
            return None


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=DUCKDB_DATABASE,
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
    config_builder.add(
        key=DUCKDB_CONFIGURATION_DICTIONARY,
        default_value=None,
        description="A valid json string with config dictionary of duckdb configuration."
        " Those are configuration options set by https://duckdb.org/docs/sql/configuration.html",
    )
