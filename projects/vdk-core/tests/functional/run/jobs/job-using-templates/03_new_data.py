# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job_input.execute_query(
        "create table vm_new_data (vm_uuid text, memory_mb int, arrival_ts text)"
    )
    job_input.execute_query(
        """
    insert into vm_new_data
values
    ('vm-33', 1500,  '2020-06-11 00:00:00'),
    ('vm-44', 3000,  '2020-06-11 00:00:00')
    """
    )
