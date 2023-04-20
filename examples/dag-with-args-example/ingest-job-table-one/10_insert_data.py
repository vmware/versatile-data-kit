# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    data_job_dir = pathlib.Path(job_input.get_job_directory())
    data_file = data_job_dir / "data.json"

    db_catalog = job_input.get_arguments().get("db_catalog")
    db_schema = job_input.get_arguments().get("db_schema")
    db_table = job_input.get_arguments().get("db_table")

    if data_file.exists():
        with open(data_file) as f:
            data = json.load(f)

        rows = [tuple(i.values()) for i in data]
        insert_query = f"""
        INSERT INTO {db_catalog}.{db_schema}.{db_table} VALUES
        """ + ", ".join(
            str(i) for i in rows
        )

        create_query = f"""
        CREATE TABLE IF NOT EXISTS {db_catalog}.{db_schema}.{db_table}
        (
            id varchar,
            first_name varchar,
            last_name varchar,
            city varchar,
            country varchar,
            phone varchar
        )
        """

        job_input.execute_query(create_query)
        job_input.execute_query(insert_query)

        print("Success! The data was send trino.")
    else:
        print("No data File Available! Exiting job execution!")
