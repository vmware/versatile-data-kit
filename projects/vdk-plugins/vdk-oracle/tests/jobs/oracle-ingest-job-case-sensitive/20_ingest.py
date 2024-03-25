# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal


def run(job_input):
    payload_same = {
        "id": 1,
        "Str_data": "string",
        "int_datA": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    payload_upper = {
        "ID": 2,
        "STR_DATA": "string",
        "INT_DATA": 12,
        "FLOAT_DATA": 1.2,
        "BOOL_DATA": True,
        "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        "DECIMAL_DATA": Decimal(0.1),
    }

    payload_lower = {
        "id": 3,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    payload_capsed = {
        "id": 4,
        "Str_data": "string",
        "Int_data": 12,
        "Float_data": 1.2,
        "Bool_data": True,
        "Timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "Decimal_data": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_same, destination_table="TEST_TABLE"
    )

    job_input.send_object_for_ingestion(
        payload=payload_lower, destination_table="TEST_TABLE"
    )

    # job_input.send_object_for_ingestion(
    #     payload=payload_upper, destination_table="test_table"
    # )

    # job_input.send_object_for_ingestion(
    #     payload=payload_capsed, destination_table="test_table"
    # )
