import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    duck_db_payload = {
        "date": "2021-01-01",
        "symbol": "BOOB",
        "price": 123.0,
    }

    job_input.send_object_for_ingestion(
        payload=duck_db_payload, destination_table="test_duckdb_table", method="duckdb", target=os.getenv("DUCKDB_DATABSE")
    )

    job_input.execute_query("CREATE TABLE stocks (date text, symbol text, price real)")

    sqlite_payload = {
        "date": "2020-01-01",
        "symbol": "GOOG",
        "price": 122.0,
    }

    job_input.send_object_for_ingestion(
        payload=sqlite_payload, destination_table="stocks", method="sqlite", target=os.getenv("VDK_SQLITE_FILE")
    )