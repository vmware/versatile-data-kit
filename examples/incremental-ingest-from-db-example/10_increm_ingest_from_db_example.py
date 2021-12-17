# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import sqlite3

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):

    # Get last_date property/parameter:
    #  - if the target table already exists, take the property value already stored in the DJ from the previous run
    #  - if the target table does not exist, set last_date to 01-01-1900 in oder to fetch all rows
    last_date = job_input.get_property("last_date", "01-01-1900")

    # Connect to sqlite local db
    os.chdir(pathlib.Path(__file__).parent.absolute())
    with sqlite3.connect("data/incremental_ingest_example.db") as db_connection:

        # Create a cursor object
        cursor = db_connection.cursor()

        # Select the needed records from the source table using a sqlite query parameter
        cursor.execute(
            f"""
            SELECT * FROM increm_ingest
            WHERE reported_date > '{last_date}'
            ORDER BY reported_date
            """
        )
        data = cursor.fetchall()

        # If any data is returned from the query, send the fetched records for ingestion
        if len(data) > 0:
            job_input.send_tabular_data_for_ingestion(
                data,
                column_names=[column_info[0] for column_info in cursor.description],
                destination_table="incremental_ingest_from_db_example",
            )

            # Reset the last_date property value to the latest date in the source db table
            job_input.set_all_properties({"last_date": max(x[2] for x in data)})

        print(f"Success! {len(data)} rows were inserted.")
