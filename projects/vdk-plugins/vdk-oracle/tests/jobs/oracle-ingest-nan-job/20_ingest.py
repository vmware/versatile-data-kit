# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload_with_types = {
        "ID": 5,
        "STR_DATA": "string",
        "INT_DATA": None,
        "FLOAT_DATA": float("nan"),
        "BOOL_DATA": True,
        "TIMESTAMP_DATA": datetime.datetime.utcfromtimestamp(1700554373),
        "DECIMAL_DATA": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="TEST_TABLE", method="oracle"
    )
