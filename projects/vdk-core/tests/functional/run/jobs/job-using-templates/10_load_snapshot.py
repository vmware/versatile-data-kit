# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    args = dict(
        source_table="vm_new_data",
        target_table="dim_vm",
        timestamp_column="arrival_ts",
        id_column="vm_uuid",
    )
    job_input.execute_template("append", args)
