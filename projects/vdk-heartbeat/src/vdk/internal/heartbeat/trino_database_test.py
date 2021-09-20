# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.database_run_test import DatabaseHeartbeatTest

log = logging.getLogger(__name__)


class TrinoDatabaseRunTest(DatabaseHeartbeatTest):
    """
    Very simple test that just waits for the job to execute once.
    """

    def __init__(self, config: Config):
        super().__init__(config)

    @staticmethod
    def _python_type_to_trino_type(column_type: Type):
        python_type_to_trino_type_map = {
            str: "varchar",
            int: "bigint",
            float: "double",
            bool: "boolean",
            datetime: "timestamp",
        }
        trino_type = python_type_to_trino_type_map.get(column_type, None)
        if trino_type:
            return trino_type
        else:
            log.warning(
                f"Cannot convert that column type : {column_type}. Will assume varchar"
                f"Current those are possible: {python_type_to_trino_type_map}"
            )
            return "varchar"

    @staticmethod
    def _python_value_to_trino_value(column_value: Any):
        if isinstance(column_value, str):
            return f"'{column_value}'"
        elif isinstance(column_value, int):
            return f"{column_value}"
        elif isinstance(column_value, float):
            return f"{column_value}"
        elif isinstance(column_value, bool):
            return f"{column_value}"
        elif isinstance(column_value, datetime):
            return f"TIMESTAMP '{column_value.isoformat(sep=' ', timespec = 'milliseconds')}'"
        log.warning(
            f"Cannot convert that column type : {type(column_value)} of value {column_value}. Will assume varchar."
        )
        return f"'{column_value}'"

    def _create_table(self, db: str, table_name: str, columns: Dict[str, Type]):
        query = f"""
        CREATE TABLE IF NOT EXISTS {db}.{table_name}(
            {",".join([k + " " + self._python_type_to_trino_type(v) for k, v in columns.items()])}
        )
        """
        # TODO: escapes?
        return self._execute_query(query)

    def _delete_table(self, db, table_name):
        query = f"drop table if exists {db}.{table_name}"
        return self._execute_query(query)

    def _insert_table_row(self, db: str, table: str, row: Dict[str, Any]):
        # TODO support partitions
        values = ",".join(
            [self._python_value_to_trino_value(v) for _, v in row.items()]
        )
        columns = ",".join([k for k, _ in row.items()])
        query = f"INSERT INTO {db}.{table} ({columns}) values ({values})"
        return self._execute_query(query)

    def _select_data(
        self, db: str, table: str, column_filters: Dict[str, str]
    ) -> List[List]:
        where_columns = " and ".join(
            [
                k + "=" + self._python_value_to_trino_value(v)
                for k, v in column_filters.items()
            ]
        )
        query = f"""select * from {db}.{table} where {where_columns}"""
        return self._execute_query(query)

    def _db_connection(self):
        from trino import dbapi
        from trino import constants

        log.debug(
            f"Open Trino Connection: host: {self.config.DATABASE_HOST}:{self.config.DATABASE_PORT} "
            f"with user: {self.config.DATABASE_USER}; "
        )
        from trino.auth import BasicAuthentication

        auth = (
            BasicAuthentication(self.config.DATABASE_USER, self.config.DATABASE_PASS)
            if self.config.DATABASE_PASS
            else None
        )
        if not self.config.DATABASE_VERIFY_SSL:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        conn = dbapi.connect(
            host=self.config.DATABASE_HOST,
            port=self.config.DATABASE_PORT,
            user=self.config.DATABASE_USER,
            auth=auth,
            catalog=None,
            schema=None,
            http_scheme=constants.HTTPS
            if self.config.DATABASE_USE_SSL
            else constants.HTTP,
            verify=self.config.DATABASE_VERIFY_SSL,
            request_timeout=self.config.DATABASE_CONNECTION_TIMEOUT_SECONDS,
        )
        return conn
