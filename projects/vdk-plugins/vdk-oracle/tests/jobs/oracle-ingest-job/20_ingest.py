# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal


def run(job_input):
    # TODO: https://github.com/vmware/versatile-data-kit/issues/2929
    # setup different data types (all passed initially as strings) are cast correctly
    # payload = {
    #     "id": "",
    #     "str_data": "string",
    #     "int_data": "12",
    #     "float_data": "1.2",
    #     "bool_data": "True",
    #     #   TODO: add timestamp
    #     #   TODO: add decimal
    # }

    # for i in range(5):
    #     local_payload = payload.copy()
    #     local_payload["id"] = i
    #     job_input.send_object_for_ingestion(
    #         payload=local_payload, destination_table="test_table"
    #     )

    payload_with_types = {
        "id": 5,
        "str_data": "string",
        "int_data": 12,
        "float_data": 1.2,
        "bool_data": True,
        "timestamp_data": datetime.datetime.fromtimestamp(1700554373),
        "decimal_data": Decimal(0.1),
    }

    job_input.send_object_for_ingestion(
        payload=payload_with_types, destination_table="test_table"
    )

    # TODO: https://github.com/vmware/versatile-data-kit/issues/2930
    # this setup:
    # a) partial payload (only few columns are included)
    # b) includes float data which is NaN
    # payload2 = {"id": 6, "float_data": math.nan, "int_data": math.nan}
    # job_input.send_object_for_ingestion(
    #     payload=payload2, destination_table="test_table"
    # )
