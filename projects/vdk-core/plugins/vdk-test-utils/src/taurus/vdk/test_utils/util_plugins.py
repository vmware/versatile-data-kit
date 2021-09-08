# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
import tempfile
import uuid
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from taurus.api.plugin.hook_markers import hookimpl
from taurus.api.plugin.plugin_input import IIngesterPlugin
from taurus.api.plugin.plugin_input import IPropertiesServiceClient
from taurus.vdk.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)
from taurus.vdk.builtin_plugins.connection.managed_cursor import ManagedCursor
from taurus.vdk.builtin_plugins.connection.pep249.interfaces import PEP249Connection
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.util.decorators import closing_noexcept_on_close

DB_TYPE_SQLITE_MEMORY = "SQLITE_MEMORY"

log = logging.getLogger(__name__)


class SqLite3MemoryDb:
    """
    Create in memory database. Each instance would generate separate db name for the in memory database.
    This way new_connection to the same instance would point the same database
    but to different one if instance is different.
    """

    def __init__(
        self, temp_directory: pathlib.Path = pathlib.Path(tempfile.gettempdir())
    ):
        self.__db_name = str(uuid.uuid4())
        self.__db_file = temp_directory.joinpath(self.__db_name + ".db")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__clean_up()

    def __del__(self):
        self.__clean_up()

    def __clean_up(self):
        try:
            self.__db_file.unlink(missing_ok=True)
        except:
            log.warning(f"cannot delete file {self.__db_file}")
            pass

    def new_connection(self):
        import sqlite3

        print(self.__db_name)
        return sqlite3.connect(f"{self.__db_file}")

    def execute_query(self, query: str) -> List[List]:
        conn = self.new_connection()
        with closing_noexcept_on_close(conn.cursor()) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


class SqLite3MemoryDbPlugin:
    def __init__(self):
        self.db = SqLite3MemoryDb()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.db.new_connection
        )


class SqLite3MemoryConnection(ManagedConnectionBase):
    def _before_cursor_execute(self, cur: ManagedCursor) -> None:
        super()._before_cursor_execute(cur)

    def __init__(self, history: List):
        super().__init__(logging.getLogger(__name__))
        self.history = history
        self.db = SqLite3MemoryDb()

    def _cursor_execute(self, cur: ManagedCursor, query: str) -> None:
        self.history.append(query)
        super()._cursor_execute(cur, query)

    def _connect(self) -> PEP249Connection:
        return self.db.new_connection()


class DecoratedSqLite3MemoryDbPlugin:
    def __init__(self):
        self.statements_history = []

    def new_connection(self) -> PEP249Connection:
        return SqLite3MemoryConnection(self.statements_history)

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.connections.add_open_connection_factory_method(
            DB_TYPE_SQLITE_MEMORY, self.new_connection
        )


class TestPropertiesServiceClient(IPropertiesServiceClient):
    """Testing properties client that keeps in memory per job properties."""

    def __init__(self):
        self._props = {}

    def read_properties(self, job_name: str) -> Dict:
        res = deepcopy(self._props.get(job_name, {}))
        return res

    def write_properties(self, job_name: str, properties: Dict) -> None:
        self._props[job_name] = deepcopy(properties)


class TestPropertiesPlugin:
    def __init__(self):
        self.properties_client = TestPropertiesServiceClient()

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        context.properties.set_properties_factory_method(
            "default", lambda: self.properties_client
        )


class IngestIntoMemoryPlugin(IIngesterPlugin):
    """
    Create a new ingestion mechanism to ingest data into memory
    """

    @dataclass
    class Payload:
        payload: List[dict]
        destination_table: Optional[str]
        target: Optional[str]
        collection_id: Optional[str]

    def __init__(self):
        self.payloads: List[IngestIntoMemoryPlugin.Payload] = []

    def ingest_payload(
        self,
        payload: List[dict],
        destination_table: Optional[str],
        target: Optional[str] = None,
        collection_id: Optional[str] = None,
    ):
        self.payloads.append(
            IngestIntoMemoryPlugin.Payload(
                payload, destination_table, target, collection_id
            )
        )

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        log.info("Initialize data job with IngestIntoMemory Plugin.")

        context.ingester.add_ingester_factory_method("memory", lambda: self)
