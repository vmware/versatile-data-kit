# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime


def run(job_input):
    payloads = [
        # do not infer columns regardless of case
        {
            "id": 1,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
            "bool_data": True,
            "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        },
        {
            "ID": 2,
            "STR_DATA": "string",
            "INT_DATA": 12,
            "FLOAT_DATA": 1.2,
            "BOOL_DATA": True,
            "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        },
        {
            "id": 3,
            "str_data": "string",
            "int_data": 12,
            "float_data": 1.2,
            "bool_data": True,
            "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        },
    ]
    for payload in payloads:
        job_input.send_object_for_ingestion(
            payload=payload, destination_table="oracle_ingest_case_insensitive"
        )
