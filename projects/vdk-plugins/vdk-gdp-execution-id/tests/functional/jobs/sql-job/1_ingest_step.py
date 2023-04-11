# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    obj = dict(product_name="name1", product_description="description1")
    job_input.send_object_for_ingestion(
        payload=obj, destination_table="object_table", method="memory"
    )

    rows = [["name2", "description2"], ["name3", "description3"]]
    job_input.send_tabular_data_for_ingestion(
        rows=rows,
        column_names=["product_name", "product_description"],
        destination_table="object_table",
        method="memory",
    )
