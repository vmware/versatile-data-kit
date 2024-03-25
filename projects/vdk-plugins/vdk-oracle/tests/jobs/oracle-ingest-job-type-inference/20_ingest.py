# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import math


def run(job_input):
    payload = {
        "ID": "5",
        "STR_DATA": "string",
        "INT_DATA": "12",
        "NAN_INT_DATA": math.nan,
        "FLOAT_DATA": "1.2",
        "BOOL_DATA": "False",
        "TIMESTAMP_DATA": "2023-11-21T08:12:53.43726",
        "DECIMAL_DATA": "0.1",
    }

    job_input.send_object_for_ingestion(payload=payload, destination_table="TEST_TABLE")
