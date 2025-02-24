# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    args = job_input.get_arguments()

    first_db = args["first_db"]
    second_db = args["second_db"]

    first_db_table = args["first_db_table"]
    second_db_table = args["second_db_table"]

    first_db_path = args["first_db_path"]
    second_db_path = args["second_db_path"]

    first_db_payload = {
        "date": "2021-01-01",
        "symbol": "BOOB",
        "price": 123.0,
    }

    job_input.execute_query(f"DROP TABLE IF EXISTS {first_db_table}", database=first_db)
    job_input.send_object_for_ingestion(
        payload=first_db_payload,
        destination_table=first_db_table,
        method=first_db,
        target=first_db_path,
    )

    first_db_payload = {
        "date": "2022-01-01",
        "symbol": "TOOT",
        "price": 124.0,
    }

    job_input.send_object_for_ingestion(
        payload=first_db_payload,
        destination_table=first_db_table,
        method=first_db,
        target=first_db_path,
    )

    job_input.execute_query(
        f"DROP TABLE IF EXISTS {second_db_table}", database=second_db
    )
    job_input.execute_query(
        f"CREATE TABLE {second_db_table} (date text, symbol text, price real)",
        database=second_db,
    )

    second_db_payload = {
        "date": "2020-01-01",
        "symbol": "GOOG",
        "price": 122.0,
    }

    job_input.send_object_for_ingestion(
        payload=second_db_payload,
        destination_table=second_db_table,
        method=second_db,
        target=second_db_path,
    )
