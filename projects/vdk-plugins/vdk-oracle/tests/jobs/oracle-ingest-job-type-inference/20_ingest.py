# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import math
from decimal import Decimal


def run(job_input):
    payload = {
        "id": "5",
        "str_data": "string",
        "int_data": "12",
        "nan_int_data": math.nan,
        "float_data": "1.2",
        "bool_data": "False",
        "timestamp_data": "2023-11-21T08:12:53",
        "decimal_data": "0.1",
    }

    job_input.send_object_for_ingestion(payload=payload, destination_table="test_table")
