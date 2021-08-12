# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import tempfile
from typing import List

from taurus.vdk.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)


class SqLiteConnection:
    """
    Create file based sqlite database.
    """

    def __init__(
        self, temp_directory: pathlib.Path = pathlib.Path(tempfile.gettempdir())
    ):
        self.__db_name = "vdk-sqlite"
        self.__db_file = temp_directory.joinpath(self.__db_name + ".db")

    def new_connection(self):
        import sqlite3

        log.info(f"Create new connection against local file db: {self.__db_name}")
        return sqlite3.connect(f"{self.__db_file}")

    def execute_query(self, query: str) -> List[List]:
        conn = self.new_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
