# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    db_catalog = job_input.get_arguments().get("db_catalog")
    db_schema = job_input.get_arguments().get("db_schema")
    db_tables = job_input.get_arguments().get("db_tables")

    job1_data = job_input.execute_query(
        f"SELECT * FROM {db_catalog}.{db_schema}.{db_tables[0]} WHERE Country NOT IN ('USA', 'Canada')"
    )
    job2_data = job_input.execute_query(
        f"SELECT * FROM {db_catalog}.{db_schema}.{db_tables[1]} WHERE Country NOT IN ('USA', 'Canada')"
    )

    print(f"Job 1 Data ===> {job1_data} \n\n\n Job 2 Data ===> {job2_data}")
