# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    data = job_input.execute_query(
        f"""
        SELECT * FROM customers_table
        """
    )

    # Fetch table info containing the column names
    table_info = job_input.execute_query("PRAGMA table_info(customers_table)")

    job_input.send_tabular_data_for_ingestion(
        data,
        column_names=[column[1] for column in table_info],
        destination_table="target_customers_table",
    )

    print(f"Success! {len(data)} rows were inserted.")
