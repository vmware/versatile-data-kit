# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job_input.execute_query("CREATE TABLE stocks (date text, symbol text, price real)")
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 123.0), ('2020-01-01', 'GOOG', 123.0)"
    )
    payload = {
        "str_col": "str",
        "int_col": 2,
        "bool_col": False,
        "dec_col": decimal.Decimal(1.234),
    }

    job_input.send_object_for_ingestion(
        payload=payload, destination_table="test_duckdb_table", method="duckdb"
    )
