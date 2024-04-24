# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload_with_types = {
        "id": 6,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.utcfromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }
    print("\n\n\n\n\n")
    print(job_input.execute_query(sql="select * from oracle_ingest", database="oracle_one"))

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="oracle_ingest", method="oracle_one", target="oracle_one"
    )
