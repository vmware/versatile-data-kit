# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import collections
import logging
import pathlib
from contextlib import closing
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import duckdb
from vdk.internal.builtin_plugins.ingestion.ingester_base import IIngesterPlugin
from vdk.internal.core import errors
from vdk.plugin.duckdb.duckdb_connection import DuckDBConnection
from vdk.plugin.sqlite.sqlite_configuration import SQLiteConfiguration

log = logging.getLogger(__name__)


class IngestToDuckDB(IIngesterPlugin):
            def ingest_payload(
            self,
            payload: List[Dict[str, Any]],
            destination_table: Optional[str] = None,
            target: str = None,
            collection_id: Optional[str] = None,
            metadata: Optional[IIngesterPlugin.IngestionMetadata] = None,
    ) -> None:

        with DuckDBConnection(target).new_connection() as conn:
            with closing(conn.cursor()) as cur:

    @staticmethod
    def __python_value_to_duckdb_type(value: Any):
        value_type = type(value)
        if value_type == bool or value_type == int:
            return "INTEGER"
        if value_type == bytes:
            return "BLOB"
        if value_type == float:
            return "REAL"
        if value_type == type(None):
            return "NULL"
        else:
            return "VARCHAR"
