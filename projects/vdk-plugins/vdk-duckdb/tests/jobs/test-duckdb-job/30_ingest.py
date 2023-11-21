# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    payload = {
        "str_col": "str",
        "int_col": 2,
        "bool_col": False,
        "dec_col": decimal.Decimal(1.234),
    }

    job_input.send_object_for_ingestion(
        payload=payload, destination_table="test_duckdb_table", method="duckdb"
    )
