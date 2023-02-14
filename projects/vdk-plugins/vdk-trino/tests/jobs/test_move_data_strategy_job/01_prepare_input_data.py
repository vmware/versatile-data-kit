# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput) -> None:
    """
    Prepare source table and insure target does not exist
    """
    args = job_input.get_arguments()
    db = args.get("db")
    src = args.get("src")
    target = args.get("target")

    job_input.execute_query(f"DROP TABLE IF EXISTS {db}.{src}")
    job_input.execute_query(f"DROP TABLE IF EXISTS {db}.{target}")
    job_input.execute_query(f"CREATE TABLE {db}.{src} (org_id INT, org_name VARCHAR)")
    job_input.execute_query(
        f"INSERT INTO {db}.{src} VALUES (1, 'first'), (2, 'second')"
    )
