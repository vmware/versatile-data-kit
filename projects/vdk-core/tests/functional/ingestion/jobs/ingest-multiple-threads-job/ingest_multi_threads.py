# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import random
import threading
import time

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    methods = ["memory1"] * 50 + ["memory2"] * 50
    random.shuffle(methods)

    threads = []
    for chosen_method in methods:
        thread = threading.Thread(
            target=ingest_data,
            args=(
                job_input,
                chosen_method,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def ingest_data(job_input: IJobInput, method: str):
    time.sleep(random.uniform(0, 0.1))
    obj = dict(
        int_key=42,
        str_key="example_str",
        bool_key=True,
        float_key=1.23,
        nested=dict(key="value"),
    )
    job_input.send_object_for_ingestion(
        payload=obj, destination_table="object_table", method=method
    )

    rows = [["two", 2], ["twenty-two", 22], ["one-eleven", 111]]
    job_input.send_tabular_data_for_ingestion(
        rows=rows,
        column_names=["first", "second"],
        destination_table="tabular_table",
        method=method,
    )
