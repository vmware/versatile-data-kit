# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload_with_types = {
        "id": 5,
        "str_data": "string",
        "int_data": None,
        "float_data": float("nan"),
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types,
        destination_table="ingest_nan_table",
        method="oracle",
    )
