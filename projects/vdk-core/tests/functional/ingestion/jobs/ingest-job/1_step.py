# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from pandas import DataFrame
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    obj = dict(
        int_key=1,
        str_key="str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )

    job_input.send_object_for_ingestion(
        payload=obj, destination_table="object_table", method="memory"
    )

    rows = [["1", 2], ["11", 22], ["111", 111]]
    job_input.send_tabular_data_for_ingestion(
        rows=rows,
        column_names=["first", "second"],
        destination_table="tabular_table",
        method="memory",
    )

    df = DataFrame.from_dict({"A": [1], "B": [2], "C": [3]})

    job_input.send_object_for_ingestion(
        payload=df, destination_table="dataframe_table", method="memory"
    )
