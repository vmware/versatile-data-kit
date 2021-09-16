# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket
import time
import uuid
from datetime import datetime
from datetime import timedelta

from retrying import retry
from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_test import HeartbeatTest
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class ImpalaDatabaseHeartbeatTest(HeartbeatTest):
    """
    The test does:
    - add record in table_source
    - wait until the Data Job copies the record
    - verify the record is in table_destination
    - truncate both tables, so they are ready for next test run

    SQL Syntax used is Impala.
    """

    def __init__(self, config: Config):
        self.config = config

        self.conn = self._db_connection()

        self.load_timestamp = int(time.time())
        self.uuid_value = uuid.uuid4()
        self.hostname = socket.gethostname()

        self.table_source = self.config.DATABASE_TEST_TABLE_SOURCE
        self.table_load_destination = self.config.DATABASE_TEST_TABLE_LOAD_DESTINATION
        self.table_destination = self.config.DATABASE_TEST_TABLE_DESTINATION

    @LogDecorator(log)
    def setup(self):
        self._execute_query(
            """
        CREATE TABLE IF NOT EXISTS {db}.{table_name}(
             uuid STRING,
             hostname STRING)
            PARTITIONED BY ( pa__arrival_ts BIGINT )
            STORED AS PARQUET;""".format(
                db=self.config.DATABASE_TEST_DB, table_name=self.table_source
            )
        )

        self._delete_old_leftover_records(self.table_source)

    @LogDecorator(log)
    def clean_up(self):
        self._clean_up_records(self.table_source)
        self._clean_up_records(self.table_destination)
        self._clean_up_records(self.table_load_destination)
        self.conn.close()

    def _db_connection(self):
        return self._build_impyla_connection(
            self.config.DATABASE_HOST,
            self.config.DATABASE_PORT,
            self.config.DATABASE_USER,
            self.config.DATABASE_PASS,
            self.config.DATABASE_AUTHN_TYPE,
            self.config.DATABASE_USE_SSL,
            self.config.DATABASE_CONNECTION_TIMEOUT_SECONDS,
        )

    @retry(stop_max_attempt_number=7, wait_exponential_multiplier=2000)
    def _execute_query(self, query):
        with self.conn.cursor() as cursor:
            log.info(f"Executing query: {query}")
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
            return res

    @staticmethod
    def _build_impyla_connection(
        the_host, the_port, the_user, the_password, mech, ssl, timeout_seconds
    ):
        from impala.dbapi import connect

        con = connect(
            host=the_host,
            port=the_port,
            use_ssl=ssl,
            auth_mechanism=mech,
            user=the_user,
            password=the_password,
            timeout=timeout_seconds,
        )
        return con

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

    def _insert_record(self):
        self._execute_query(
            """INSERT INTO TABLE {db}.{table} PARTITION (pa__arrival_ts={ts}) values ('{uuid}', '{hostname}');""".format(
                db=self.config.DATABASE_TEST_DB,
                table=self.table_source,
                ts=self.load_timestamp,
                uuid=self.uuid_value,
                hostname=self.hostname,
            )
        )

    def _get_records_from_dest_table(self, query_src):
        return self._execute_query(
            """SELECT COUNT(*)
            FROM {db}.{dest_table}
            WHERE pa__arrival_ts = {ts}
               AND query_source = '{query_src}'
               AND uuid = '{uuid_value}'
               AND hostname = '{hostname}';""".format(
                db=self.config.DATABASE_TEST_DB,
                dest_table=self.table_destination,
                ts=self.load_timestamp,
                query_src=query_src,
                uuid_value=self.uuid_value,
                hostname=self.hostname,
            )
        )

    def _get_records_from_load_dest_table(self):
        return self._execute_query(
            """SELECT COUNT(*)
            FROM {db}.{dest_table}
            WHERE pa__arrival_ts = {ts}
               AND uuid = '{uuid_value}'
               AND hostname = '{hostname}';""".format(
                db=self.config.DATABASE_TEST_DB,
                dest_table=self.table_load_destination,
                ts=self.load_timestamp,
                uuid_value=self.uuid_value,
                hostname=self.hostname,
            )
        )

    def _clean_up_records(self, table):
        log.info(f"Deleting table: {table}")
        try:
            self._execute_query(
                """drop table {db}.{table};""".format(
                    db=self.config.DATABASE_TEST_DB, table=table
                )
            )
        except Exception as e:
            log.warning(
                f"Failed to clean up test table {table} "
                f"Exception {e}"
                "There maybe some left-overs in the database that need to be clean manually."
            )

    @LogDecorator(log)
    def execute_test(self):
        self._insert_record()
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
                py_record_count = py_result[0][0]
                sql_result = self._get_records_from_dest_table("sql")
                sql_record_count = sql_result[0][0]
                load_result = self._get_records_from_load_dest_table()
                load_record_count = load_result[0][0]

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
            f"destination table {self.table_load_destination} not updated by python (20_move_data.py)",
        )
        log.info("Database test verification passed successfully.")

    def assertTrue(self, condition, error, exception=None):
        msg = (
            "What: Database test failed.\n"
            "Why: Error was {}. "
            f"Most probably, the heartbeat data job (name: {self.config.job_name}) "
            f"failed during this test execution or there were Database related issues.\n"
            "Consequences: Test failure indicates an issue with Control Service deployment or VDK-Core -"
            " a regression or infrastructure dependency issue.\n"
            "Countermeasures: Check the error message. Check the Data Job status and logs in Kubernetes. "
            " Check if VDK Control service or VDK-Core have not regressed.\n"
        )
        if condition:
            log.info("Database test is successful.")
        else:
            if exception:
                log.exception(exception)
            raise AssertionError(msg.format(error), exception)
