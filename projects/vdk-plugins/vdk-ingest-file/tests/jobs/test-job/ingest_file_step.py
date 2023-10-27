# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    test_destination_table: str = job_input.get_arguments().get(
        "test_destination_table", "test_table"
    )
    test_object = {
        "@table": test_destination_table,
        "@id": "test_id",
        "some_data": "some_test_data",
    }
    test_payload = [{**test_object, "index": i} for i in range(10)]

    test_method: str = job_input.get_arguments().get("test_method", "test_method")
    test_target: str = job_input.get_arguments().get("test_target", "test_target")
    test_collection_id: str = "test_collection_id"

    for obj in test_payload:
        job_input.send_object_for_ingestion(
            payload=obj,
            destination_table=test_destination_table,
            method=test_method,
            target=test_target,
            collection_id=test_collection_id,
        )
