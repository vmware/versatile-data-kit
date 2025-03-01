# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    obj = dict(
        int_key=42,
        str_key="example_str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )

    job_input.send_object_for_ingestion(
        payload=obj, destination_table="object_table", method="memory"
    )

    rows = [["two", 2], ["twenty-two", 22], ["one-eleven", 111]]
    job_input.send_tabular_data_for_ingestion(
        rows=rows,
        column_names=["first", "second"],
        destination_table="tabular_table",
        method="memory",
    )
