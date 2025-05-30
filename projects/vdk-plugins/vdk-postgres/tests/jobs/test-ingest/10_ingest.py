# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0


def run(job_input):
    payload = {
        "some_data": "some_test_data",
        "more_data": "more_test_data",
        "int_data": 11,
        "float_data": 3.14,
        "bool_data": True,
    }

    for _ in range(5):
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_table"
        )
