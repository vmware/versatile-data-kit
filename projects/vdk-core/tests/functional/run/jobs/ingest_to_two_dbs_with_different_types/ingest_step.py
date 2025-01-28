# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    duck_db_payload = {
        "date": "2021-01-01",
        "symbol": "BOOB",
        "price": 123.0,
    }

    job_input.send_object_for_ingestion(
        payload=duck_db_payload,
        destination_table="test_duckdb_table",
        method="duckdb",
        target=os.getenv("DUCKDB_DATABASE"),
    )

    duck_db_payload = {
        "date": "2022-01-01",
        "symbol": "TOOT",
        "price": 124.0,
    }

    # we do not need to specify the target here since DUCKDB is set as default with nv var VDK_INGEST_TARGET_DEFAULT

    job_input.send_object_for_ingestion(
        payload=duck_db_payload, destination_table="test_duckdb_table", method="duckdb"
    )

    job_input.execute_query("CREATE TABLE stocks (date text, symbol text, price real)")

    sqlite_payload = {
        "date": "2020-01-01",
        "symbol": "GOOG",
        "price": 122.0,
    }

    job_input.send_object_for_ingestion(
        payload=sqlite_payload,
        destination_table="stocks",
        method="sqlite",
        target=os.getenv("VDK_SQLITE_FILE"),
    )
