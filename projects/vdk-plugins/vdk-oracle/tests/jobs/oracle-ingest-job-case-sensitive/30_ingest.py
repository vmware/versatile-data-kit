# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal
from time import sleep


def run(job_input):
    payload_lower = {
        "ID": 2,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    payload_upper = {
        "ID": 1,
        "STR_DATA": "string",
        "INT_DATA": 12,
        "FLOAT_DATA": 1.2,
        "BOOL_DATA": True,
        "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        "DECIMAL_DATA": Decimal(0.1),
    }

    payload_caps = {
        "ID": 3,
        "Str_Data": "string",
        "Int_Data": 12,
        "Float_Data": 1.2,
        "Bool_Data": True,
        "Timestamp_Data": datetime.datetime.utcfromtimestamp(1700554373),
        "Decimal_Data": Decimal(0.1),
    }

    # Ingests without inferring anything, because columns match what's in TEST_TABLE
    job_input.send_object_for_ingestion(
        payload=payload_upper, destination_table="TEST_TABLE"
    )

    sleep(5)
    # vdk-oracle treats all identifiers as case-sensitive
    # this will create a new table, because TEST_TABLE != test_table
    job_input.send_object_for_ingestion(
        payload=payload_upper, destination_table="test_table"
    )

    sleep(5)
    # infers and creates a bunch of new columns in TEST_TABLE
    # because identifiers are case-sensitive
    # STR_DATA != str_data
    job_input.send_object_for_ingestion(
        payload=payload_lower, destination_table="TEST_TABLE"
    )

    sleep(5)
    # infers and creates a bunch of new columns in test_table
    # because identifiers are case-sensitive
    # STR_DATA != Str_Data
    job_input.send_object_for_ingestion(
        payload=payload_caps, destination_table="test_table"
    )
