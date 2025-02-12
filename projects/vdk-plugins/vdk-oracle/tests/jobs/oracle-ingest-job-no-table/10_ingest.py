# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal


def run(job_input):
    col_names = [
        "id",
        "str_data",
        "int_data",
        "float_data",
        "bool_data",
        "timestamp_data",
        "decimal_data",
    ]
    row_data = [
        [
            0,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.utcfromtimestamp(1700554373),
            Decimal(1.1),
        ],
        [
            1,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.utcfromtimestamp(1700554373),
            Decimal(1.1),
        ],
        [
            2,
            "string",
            12,
            1.2,
            True,
            datetime.datetime.utcfromtimestamp(1700554373),
            Decimal(1.1),
        ],
    ]
    job_input.send_tabular_data_for_ingestion(
        rows=row_data, column_names=col_names, destination_table="ingest_no_table"
    )
