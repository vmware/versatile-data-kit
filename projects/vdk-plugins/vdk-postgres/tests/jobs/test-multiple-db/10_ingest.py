# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job_input.execute_query(
        sql="CREATE TABLE multiple_default_db_test "
        "(some_data varchar, more_data varchar, "
        "int_data bigint, float_data real, bool_data boolean)",
        database="postgres",
    )

    job_input.execute_query(
        sql="CREATE TABLE multiple_db_test "
        "(some_data varchar, more_data varchar, "
        "int_data bigint, float_data real, bool_data boolean)",
        database="postgres_second",
    )

    payload = {
        "some_data": "some_test_data",
        "more_data": "more_test_data",
        "int_data": 11,
        "float_data": 3.14,
        "bool_data": True,
    }

    for _ in range(5):
        job_input.send_object_for_ingestion(
            payload=payload,
            destination_table="multiple_default_db_test",
            method="postgres",
            target="postgres",
        )

    payload = {
        "some_data": "some_test_data",
        "more_data": "more_test_data",
        "int_data": 12,
        "float_data": 3.14,
        "bool_data": False,
    }

    for _ in range(5):
        job_input.send_object_for_ingestion(
            payload=payload,
            destination_table="multiple_db_test",
            method="postgres_second",
            target="postgres_second",
        )
