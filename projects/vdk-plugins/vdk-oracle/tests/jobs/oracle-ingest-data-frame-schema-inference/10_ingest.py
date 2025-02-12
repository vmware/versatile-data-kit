# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from pandas import DataFrame
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    df = DataFrame.from_dict({"a": [1], "b": [2], "c": [3]})

    job_input.send_object_for_ingestion(
        payload=df, destination_table="data_frame_schema_inference"
    )
