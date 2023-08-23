# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import tempfile
from typing import List

import duckdb
from vdk.internal.util.decorators import closing_noexcept_on_close

log = logging.getLogger(__name__)


class DuckDBConnection:
    """
    Create file based DuckDB database.
    """

    def __init__(
        self,
        duckdb_file: pathlib.Path = pathlib.Path(tempfile.gettempdir()).joinpath(
            "vdk-duckdb.db"
        ),
    ):
        self.__db_file = duckdb_file

    def new_connection(self):
        log.info(
            f"Creating new connection against local file database located at: {self.__db_file}"
        )
        return duckdb.connect(f"{self.__db_file}")

    def execute_query(self, query: str) -> List[List]:
        conn = self.new_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
