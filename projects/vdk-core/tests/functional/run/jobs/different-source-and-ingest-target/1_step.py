# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job_input.execute_query("CREATE TABLE stocks (date text, symbol text, price real)")
    job_input.execute_query("INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 122.0)")
    result = job_input.execute_query("SELECT * FROM stocks")
    payload = {
        "date": result[0][0],
        "symbol": result[0][1],
        "price": 500,
    }

    job_input.send_object_for_ingestion(
        payload=payload, destination_table="test_duckdb_table", method="duckdb"
    )
