# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import tempfile
from typing import List

from taurus.vdk.core.config import Configuration
from taurus.vdk.util.decorators import closing_noexcept_on_close

SQLITE_FILE = "SQLITE_FILE"

log = logging.getLogger(__name__)


class SQLiteConfiguration:
    def __init__(self, configuration: Configuration):
        self.__config = configuration

    def get_default_ingest_target(self) -> pathlib.Path:
        return pathlib.Path(self.__config.get_value("INGEST_TARGET_DEFAULT"))

    def get_sqlite_file(self) -> pathlib.Path:
        return pathlib.Path(self.__config.get_value(SQLITE_FILE))


class SQLiteConnection:
    """
    Create file based sqlite database.
    """

    def __init__(
        self,
        sqlite_file: pathlib.Path = pathlib.Path(tempfile.gettempdir()).joinpath(
            "vdk-sqlite.db"
        ),
    ):
        self.__db_file = sqlite_file

    def new_connection(self):
        import sqlite3

        log.info(
            f"Creating new connection against local file database located at: {self.__db_file}"
        )
        return sqlite3.connect(f"{self.__db_file}")

    def execute_query(self, query: str) -> List[List]:
        conn = self.new_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
