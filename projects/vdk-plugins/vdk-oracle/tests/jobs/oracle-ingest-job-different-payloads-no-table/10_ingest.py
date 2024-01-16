# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime


def run(job_input):
    payloads = [
        {
            "id": 0,
        },
        {
            "id": 1,
            "str_data": "string",
        },
        {
            "id": 2,
            "str_data": "string",
            "int_data": 12,
        },
        {
            "id": 3,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
        },
        {
            "id": 4,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
            "bool_data": True,
        },
        {
            "id": 5,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
            "bool_data": True,
            "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        },
        {
            "id": 6,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
        },
        {
            "id": 7,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
            "bool_data": True,
        },
    ]
    for payload in payloads:
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="test_table"
        )
