# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from pandas import DataFrame
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    df = DataFrame.from_dict({"A": [1], "B": [2], "C": [3]})

    job_input.send_object_for_ingestion(payload=df, destination_table="test_table")
