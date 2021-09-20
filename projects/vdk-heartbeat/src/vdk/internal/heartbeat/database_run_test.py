# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket
import time
import uuid
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List

from retrying import retry
from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_test import HeartbeatTest
from vdk.internal.heartbeat.tracing import LogDecorator
from vdk.internal.heartbeat.util import closing_noexcept_on_close

log = logging.getLogger(__name__)


class DatabaseHeartbeatTest(HeartbeatTest):
    """
    The test does:
    - add record in table_source
    - wait until the Data Job copies the record
    - verify the record is in table_destination
    - truncate both tables, so they are ready for next test run

    Subclass and implement the abstractmethod
    """

    def __init__(self, config: Config):
        super().__init__(config)

        self.conn = self._db_connection()

        self.load_timestamp = datetime.utcnow()
        self.uuid_value = uuid.uuid4()
        self.hostname = socket.gethostname()

        self.table_source = self.config.DATABASE_TEST_TABLE_SOURCE
        self.table_destination = self.config.DATABASE_TEST_TABLE_DESTINATION

    @abstractmethod
    def _create_table(self, db: str, table_name: str, columns: Dict):
        """
        Create table
        :param db: the database or schema name
        :param table_name: table
        :param columns: what columns to create in format dict [ name, python type ]
        :return: result of create table, raise on error
        """
        pass

    @abstractmethod
    def _delete_table(self, db, table_name):
        """
        Delete or drop table
        :param db: the database or schema name
        :param table_name: table
        :return: result of create table, raise on error
        """
        pass

    @abstractmethod
    def _insert_table_row(self, db: str, table: str, row: Dict[str, Any]):
        """
        Insert single row into a table
        :param db: the database or schema name
        :param table_name: table
        :param row: the row to insert in format dict [ column_name, value ]
        :return: result of create table, raise on error
        """
        pass

    @abstractmethod
    def _select_data(
        self, db: str, table: str, column_filters: Dict[str, str]
    ) -> List[List]:
        """
        select data from a table (select * from db.table where column_filers ...)
        :param db: the database or schema name
        :param table_name: table
        :param column_filters: to be added in where, where key=value and key2=value2; for simpliciy are assumed to be string
        so impl should cast them
        :return: result in tabular format
        """
        pass

    @abstractmethod
    def _db_connection(self):
        """Return DB API Connection"""
        pass

    @LogDecorator(log)
    def setup(self):
        log.info(f"create table {self.config.DATABASE_TEST_DB}.{self.table_source}")
        self._create_table(
            db=self.config.DATABASE_TEST_DB,
            table_name=self.table_source,
            columns={"uuid": str, "hostname": str, "pa__arrival_ts": datetime},
        )

        row = dict(
            pa__arrival_ts=self.load_timestamp,
            uuid=self.uuid_value,
            hostname=self.hostname,
        )
        log.info(
            f"insert initial row into source table {self.config.DATABASE_TEST_DB}.{self.table_source}: {row}"
        )
        self._insert_table_row(
            db=self.config.DATABASE_TEST_DB, table=self.table_source, row=row
        )

    def __exit__(self, *exc):
        self.clean_up()

    @LogDecorator(log)
    def clean_up(self):
        self._clean_up_records(self.config.DATABASE_TEST_DB, self.table_source)
        self._clean_up_records(self.config.DATABASE_TEST_DB, self.table_destination)
        self.conn.close()

    @retry(stop_max_attempt_number=7, wait_exponential_multiplier=2000)
    def _execute_query(self, query):
        with closing_noexcept_on_close(self.conn.cursor()) as cursor:
            log.info(f"Executing query: {query}")
            try:
                cursor.execute(query)
                try:
                    res = cursor.fetchall()
                except Exception as pe:
                    res = None
                    if str(pe) in (
                        "No results.  Previous SQL was not a query.",  # message in pyodbc
                        "Trying to fetch results on an operation with no results.",  # message in impyla
                        "no results to fetch",  # psycopg: ProgrammingError: no results to fetch
                    ):
                        log.debug(
                            "Fetching all results from query SUCCEEDED. Query does not produce results (e.g. DROP TABLE)."
                        )
                    else:
                        log.debug("Fetching all results from query FAILED.")
                        raise
            except Exception as query_ex:
                log.info(f"Exception was thrown while executing query: {query_ex}")
                raise
            return res

    def _delete_old_leftover_records(self, table):
        log.info(
            "Deleting leftover records from previous tests in table: {table}".format(
                table=table
            )
        )
        one_day_ago_ts = datetime.now() - timedelta(days=1)
        one_day_ago_ts = int(time.mktime(one_day_ago_ts.timetuple()))
        self._execute_query(
            """alter table {db}.{table} drop if exists partition (pa__arrival_ts < {ts});""".format(
                db=self.config.DATABASE_TEST_DB, table=table, ts=one_day_ago_ts
            )
        )

    def _get_records_from_dest_table(self, query_source) -> List[List]:
        return self._select_data(
            db=self.config.DATABASE_TEST_DB,
            table=self.table_destination,
            column_filters=dict(
                query_source=query_source, uuid=self.uuid_value, hostname=self.hostname
            ),
        )

    def _clean_up_records(self, db, table):
        log.info(f"Deleting table: {db}.{table}")
        try:
            self._delete_table(db, table)
        except Exception as e:
            log.warning(
                f"Failed to clean up test table {table} "
                f"Exception {e}"
                "There maybe some left-overs in the database that need to be clean manually."
            )

    @LogDecorator(log)
    def execute_test(self):
        self.wait_for_results_and_verify()

    def wait_for_results_and_verify(self):
        wait_time_seconds = 30
        start_time = time.time()
        record_count = 0
        expected_record_count = 3
        caught_exception = None
        while (
            record_count < expected_record_count
            and time.time() - start_time < self.config.RUN_TEST_TIMEOUT_SECONDS
        ):

            log.info(f"Search for records with uuid = {self.uuid_value}")
            caught_exception = None
            try:
                py_result = self._get_records_from_dest_table("python")
                py_record_count = len(py_result)
                sql_result = self._get_records_from_dest_table("sql")
                sql_record_count = len(sql_result)
                load_result = self._get_records_from_dest_table("load")
                load_record_count = len(load_result)

                record_count = py_record_count + sql_record_count + load_record_count

                if record_count != expected_record_count:
                    log.info(
                        "Records are not available yet. Waiting {} seconds before trying again.".format(
                            wait_time_seconds
                        )
                    )
                    time.sleep(wait_time_seconds)
            except Exception as e:
                caught_exception = e

                log.info(
                    "Error while querying for results. Waiting {} seconds before trying again.".format(
                        wait_time_seconds
                    )
                )
                time.sleep(wait_time_seconds)

        self.assertTrue(
            caught_exception is None,
            f"verification failed with {caught_exception}",
            caught_exception,
        )
        # We expect to have 1 record coming from python script and 1 record coming from sql script.
        # (>=, because the heartbeat job, could have been executed more than once)

        self.assertTrue(
            int(py_record_count) >= 1,
            f"destination table {self.table_destination} not updated by python (20_move_data.py)",
        )
        self.assertTrue(
            int(sql_record_count) >= 1,
            f"destination table {self.table_destination} not updated by SQL (30_move_data.sql)",
        )
        self.assertTrue(
            int(load_record_count) >= 1,
            f"destination table {self.table_destination} not updated by python load (20_move_data.py)",
        )
        log.info("Database test verification passed successfully.")

    def assertTrue(self, condition, error, exception=None):
        msg = (
            "\nWhat: Database test failed.\n"
            f"Why: Error was {error}."
            f"Most probably, the heartbeat data job (name: {self.config.job_name}) "
            f"failed during this test execution or there were Database related issues.\n"
            "Consequences: Test failure indicates an issue with Control Service deployment or SDK -"
            " a regression or infrastructure dependency issue.\n"
            "Countermeasures: Check the error message. Check the Data Job status and logs in Kubernetes. "
            " Check if Control service or VDK have not regressed.\n"
        )
        if condition:
            log.info("Database test is successful.")
        else:
            if exception:
                raise AssertionError(msg) from exception
            else:
                raise AssertionError(msg)
