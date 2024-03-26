# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import re
import sys
import time
from typing import cast
from typing import Optional
from typing import Tuple

import sqlparse
from impala._thrift_gen.RuntimeProfile.ttypes import TRuntimeProfileFormat
from impala.hiveserver2 import HiveServer2Cursor
from vdk.api.lineage.model.logger.lineage_logger import ILineageLogger
from vdk.api.lineage.model.sql.model import LineageData
from vdk.api.lineage.model.sql.model import LineageTable
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.core.statestore import StoreKey

LINEAGE_LOGGER_KEY = StoreKey[ILineageLogger]("impala-lineage-logger")

log = logging.getLogger(__name__)


class ImpalaLineage:
    """
    Calculates lineage information from the query plan of executed queries.
    Lineage is calculated only if the query has finished successfully and has resulted actual data read or write from/to
    the underlying storage.
    """

    def __init__(self, lineage_logger: ILineageLogger = None):
        self._lineage_logger = lineage_logger

    def calculate_lineage(self, execution_cursor: ExecutionCursor) -> None:
        try:
            if self._lineage_logger and sys.version_info < (3, 10):
                # calculate and send lineage data only if there is a registered lineage logger
                # at the time of writing SystemError occurs "PY_SSIZE_T_CLEAN macro must be defined for '#' formats"
                # when trying to calculate lineage information, TODO resolve the above error for python 3.10
                hive_cursor = cast(HiveServer2Cursor, execution_cursor)
                lineage_data = self._get_lineage_data(hive_cursor)
                if (
                    lineage_data
                ):  # some queries do not have data lineage - select 1, create table, compute stats, etc
                    self._lineage_logger.send(lineage_data)
        # do not stop job execution if error occurs during lineage processing
        except Exception:
            log.warning(
                "Error occurred during lineage calculation. No lineage information will be generated."
                " Job execution will continue",
                exc_info=True,
            )

    def _get_lineage_data(self, cursor: HiveServer2Cursor) -> Optional[LineageData]:
        query_statement = cursor._cursor.query_string
        if not self._does_query_have_lineage(query_statement):
            return None  # do not capture lineage for queries that don't have lineage information
        start_time = time.time_ns()
        query_profile = cursor.get_profile(profile_format=TRuntimeProfileFormat.STRING)
        end_time = time.time_ns()
        log.debug(
            "Successfully retrieved query profile to calculate data lineage for last executed query."
            f"Time taken to retrieve profile: {(end_time - start_time) / 1000000} milliseconds t"
            f"Profile size: {sys.getsizeof(query_profile)} bytes"
        )
        if "Query Status: OK" not in query_profile:
            return None  # do not capture lineage for failed queries
        inputs, output = self._parse_inputs_outputs(query_profile)
        if not inputs and not output:
            return None  # no lineage was present in the query plan, e.g. select 1 query
        return LineageData(
            query=query_statement,
            query_status="OK",
            query_type=None,  # TODO specify query_type once there is clear spec for it
            input_tables=[
                self._get_lineage_table_from_table_name(table_name)
                for table_name in inputs
            ],
            output_table=self._get_lineage_table_from_table_name(output),
        )

    @staticmethod
    def _does_query_have_lineage(query_statement: str) -> bool:
        """
        This method checks the query type because not every query
        has information that could be classified as lineage data
        and making an extra query for the profile is unnecessary

        This method does not provide absolute certainty for
        containing lineage data, but it does skip a certain
        queries which are known to be non-lineage
        """
        if query_statement is None:
            return False

        query_statement = query_statement.lower()
        # managed_connection has a way to open and check connections with keep alive query
        if "select 1 -- testing if connection is alive." in query_statement:
            return False

        query_statement = sqlparse.format(
            sql=query_statement,
            strip_comments=True,
            strip_whitespace=True,
            keyword_case="lower",
        )

        if query_statement.startswith("create"):
            # some create statements might have lineage
            # (create table .. as select ..) this way we check
            # if select is present in some form. This might result
            # in some corner cases of false positive, but the
            # profile of impala will not return any lineage
            # info (scan/write hdfs) as our goal of this method is
            # to reduce non-lineage query with a non-complex way
            return (
                "select " in query_statement or "select" + os.linesep in query_statement
            )
        if query_statement.startswith(
            (
                "alter",
                "compute",
                "describe",
                "drop",
                "explain",
                "grant",
                "invalidate",
                "refresh",
                "revoke",
                "set",
                "show",
                "truncate",
                "use",
            )
        ):
            # these commands are not providing lineage data in the profile at the moment
            return False

        return True

    @staticmethod
    def _parse_inputs_outputs(query_profile: str) -> Tuple[list, str]:
        inputs = []
        output = None
        for line in query_profile.splitlines():
            match = re.search(r"(?<=SCAN HDFS \[)[\w\.]*", line)
            if match:
                inputs.append(match.group(0))
            else:
                match = re.search(r"(?<=WRITE TO HDFS \[)[\w\.]*", line)
                if match:
                    output = match.group(0)
        return list(set(inputs)), output

    @staticmethod
    def _get_lineage_table_from_table_name(
        table_name: Optional[str],
    ) -> Optional[LineageTable]:
        if table_name is None:
            return None
        split_name = table_name.split(".")
        return LineageTable(schema=split_name[0], table=split_name[1], catalog=None)
