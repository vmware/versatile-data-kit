# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal


def run(job_input):
    payload_with_types = {
        "ID": 5,
        "@STR_DATA": "string",
        "%INT_DATA": 12,
        "*FLOAT*DATA*": 1.2,
        "BOOL_DATA": True,
        "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        "DECIMAL_DATA": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="TEST_TABLE"
    )
