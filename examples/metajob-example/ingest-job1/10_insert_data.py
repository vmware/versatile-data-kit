# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    data_job_dir = pathlib.Path(job_input.get_job_directory())
    data_file = data_job_dir / "data.json"

    if data_file.exists():
        with open(data_file) as f:
            data = json.load(f)

        rows = [tuple(i.values()) for i in data]
        insert_query = """
        INSERT INTO memory.default.test_metajob_one VALUES
        """ + ", ".join(
            str(i) for i in rows
        )

        job_input.execute_query(
            """
            CREATE TABLE IF NOT EXISTS memory.default.test_metajob_one
            (
                id varchar,
                first_name varchar,
                last_name varchar,
                city varchar,
                country varchar,
                phone varchar
            )
            """
        )

        job_input.execute_query(insert_query)

        print("Success! The data was send trino.")
    else:
        print("No data File Available! Exiting job execution!")
