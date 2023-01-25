# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import tempfile
from typing import List

from vdk.internal.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)


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
        return sqlite3.connect(f"{self.__db_file}", isolation_level=None)

    def execute_query(self, query: str) -> List[List]:
        conn = self.new_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
