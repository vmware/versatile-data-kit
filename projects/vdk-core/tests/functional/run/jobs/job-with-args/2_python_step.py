# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    counter = job_input.get_arguments().get("counter")
    job_input.execute_query(f"insert into {{table_name}} VALUES ('one', {counter})")
