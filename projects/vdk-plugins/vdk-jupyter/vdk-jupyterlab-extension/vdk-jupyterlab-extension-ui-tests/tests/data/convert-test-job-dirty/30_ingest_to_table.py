# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sqlite3


def run(job_input):
    db_connection = sqlite3.connect(
        "chinook.db"
    )  # if chinook.db file is not in your current directory, replace "chinook.db" with the path to your chinook.db file
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM employees")
    job_input.send_tabular_data_for_ingestion(
        cursor,
        column_names=[column_info[0] for column_info in cursor.description],
        destination_table="backup_employees",
    )
