# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload = {
        "str_col": "str",
        "int_col": 2,
        "bool_col": False,
        "time": job_input.get_arguments().get("time"),
    }

    for i in range(10):
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_vdk_table", method="huggingface"
        )
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_vdk_table2", method="huggingface"
        )
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_vdk_table3", method="huggingface"
        )
