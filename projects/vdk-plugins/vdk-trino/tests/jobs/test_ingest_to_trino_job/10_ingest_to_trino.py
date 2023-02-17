# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import math


def run(job_input):
    # setup different data types (all passed initially as strings) are cast correctly
    payload = {
        "str_data": "string",
        "int_data": "12",
        "float_data": "1.2",
        "bool_data": "True",
        "decimal_data": "3.2",
    }

    for i in range(5):
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_table"
        )

    payload_with_types = {
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "decimal_data": 3.2,
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="test_table"
    )

    # this setup:
    # a) partial payload (only few columns are included)
    # b) includes float data which is NaN
    payload2 = {"float_data": math.nan, "decimal_data": math.nan}
    job_input.send_object_for_ingestion(
        payload=payload2, destination_table="test_table"
    )
