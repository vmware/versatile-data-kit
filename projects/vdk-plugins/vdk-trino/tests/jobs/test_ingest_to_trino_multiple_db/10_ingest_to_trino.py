# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0


def run(job_input):
    # against the default db
    job_input.execute_query(sql="DROP TABLE IF EXISTS test_table")
    job_input.execute_query(
        sql="CREATE TABLE IF NOT EXISTS test_table "
        "("
        "str_data varchar, "
        "int_data bigint,"
        "float_data double,"
        "bool_data boolean,"
        "decimal_data decimal(4,2)"
        ")"
    )
    payload_with_types = {
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "decimal_data": 3.2,
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="test_table"
    )

    # against the secondary db
    job_input.execute_query(
        sql="DROP TABLE IF EXISTS secondary_test_table", database="trino_second"
    )
    job_input.execute_query(
        sql="CREATE TABLE IF NOT EXISTS secondary_test_table "
        "("
        "str_data varchar, "
        "int_data bigint,"
        "float_data double,"
        "bool_data boolean,"
        "decimal_data decimal(4,2)"
        ")",
        database="trino_second",
    )
    payload_with_types = {
        "str_data": "string",
        "int_data": 13,
        "float_data": 1.2,
        "bool_data": False,
        "decimal_data": 3.2,
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types,
        destination_table="secondary_test_table",
        method="trino_second",
    )
