# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job1_data = job_input.execute_query("SELECT * FROM memory.default.test_airflow_one")
    job2_data = job_input.execute_query("SELECT * FROM memory.default.test_airflow_two")

    print(f"Job 1 Data ===> {job1_data} \n\n\n Job 2 Data ===> {job2_data}")
