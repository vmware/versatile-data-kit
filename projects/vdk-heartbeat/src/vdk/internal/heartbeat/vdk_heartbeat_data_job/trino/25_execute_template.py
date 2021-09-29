# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import uuid


log = logging.getLogger(__name__)


def run(job_input):
    # This step is prefixed with '25_' because it is important that it is executed before the last step.
    # vdk-heartbeat currently finishes successfully after wait_for_results_and_verify verifies that the expected
    # data was successfully moved in step 30_move_data_using_sql.sql - this is why execute_template step
    # must be placed before that.

    if job_input.get_property("execute_template") == "False":
        log.info(f"Skipping Trino template execution test.")
        return

    ts = uuid.uuid4().hex

    # If db property includes catalog name, get only the schema name ('default' from 'memory.default').
    # This is done because the templates' implementation escapes db, table and column names passed as arguments, so that
    # reserved words could be used for their values
    db_name = job_input.get_property("db").split(".")[-1]

    target_table = f"vdk_heartbeat_template_dim_users_{ts}"
    source_table = f"vdk_heartbeat_template_vw_dim_users_{ts}"

    try:
        run_template_test(job_input, db_name, target_table, source_table)
    finally:
        job_input.execute_query(f"DROP TABLE IF EXISTS {db_name}.{target_table}")
        job_input.execute_query(f"DROP TABLE IF EXISTS {db_name}.{source_table}")


def run_template_test(job_input, db_name, target_table, source_table):
    # prepare source data
    job_input.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {db_name}.{source_table}
        (
            id varchar,
            name varchar,
            username varchar,
            email varchar
        )
        """
    )
    job_input.execute_query(
        f"""
        INSERT INTO {db_name}.{source_table} VALUES
            ('id', 'A. Userov',  'auserov', 'auserov@example.com')
        """
    )

    # prepare target table
    job_input.execute_query(
        f"""
        DROP TABLE IF EXISTS {db_name}.{target_table}
        """
    )
    job_input.execute_query(
        f"""
        CREATE TABLE {db_name}.{target_table} (
            LIKE {db_name}.{source_table}
        )
        """
    )

    # execute template which will copy data from source to target
    template_args = {
        "target_schema": db_name,
        "target_table": target_table,
        "source_schema": db_name,
        "source_view": source_table,
    }
    job_input.execute_template(template_name="scd1", template_args=template_args)

    # check if target was correctly populated (only 1 entry from source should be inserted there)
    result = job_input.execute_query(f"SELECT COUNT (1) FROM {db_name}.{target_table}")

    if result and result[0][0] != 1:
        raise Exception("scd1 template did not work correctly.")
