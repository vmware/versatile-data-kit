# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import time
import uuid


def run(job_input):
    ts = uuid.uuid4().hex
    db = job_input.get_property("db")
    table = f"vdk_heartbeat_dim_users_{ts}"
    view = f"vdk_heartbeat_vw_dim_users_{ts}"
    try:
        run_template_test(job_input, db, table, view)
    finally:
        job_input.execute_query(f"drop table {db}.{table}")
        job_input.execute_query(f"drop view {db}.{view}")


def run_template_test(job_input, db, table, view):
    job_input.execute_query(
        f"""
   CREATE TABLE IF NOT EXISTS {db}.{table}
   (
        id string,
        name string,
        username string,
        email string
    )
    stored as parquet
   """
    )
    job_input.execute_query(
        f"""
    CREATE VIEW IF NOT EXISTS {db}.{view} AS
        SELECT 'id', 'A. Userov',  'auserov', 'auserov@example.com'
   """
    )
    template_args = {
        "target_schema": db,
        "target_table": table,
        "source_schema": db,
        "source_view": view,
        "staging_schema": db,
    }
    job_input.execute_template(
        template_name="load/dimension/scd1", template_args=template_args
    )
    job_input.execute_query(f"select * from {db}.{table}")
