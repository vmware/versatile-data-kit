# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime


def run(job_input):
    payloads = [
        {
            "ID": 0,
        },
        {
            "ID": 1,
            "STR_DATA": "string",
        },
        {
            "ID": 2,
            "STR_DATA": "string",
            "INT_DATA": 12,
        },
        {
            "ID": 3,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
        },
        {
            "ID": 4,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
            "BOOL_DATA": True,
        },
        {
            "ID": 5,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
            "BOOL_DATA": True,
            "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        },
        {
            "ID": 6,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
        },
        {
            "ID": 7,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
            "BOOL_DATA": True,
        },
    ]
    for payload in payloads:
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="TEST_TABLE"
        )
