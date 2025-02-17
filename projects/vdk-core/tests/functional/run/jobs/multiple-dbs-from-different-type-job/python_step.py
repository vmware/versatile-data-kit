# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    job_input.execute_query(
        "CREATE TABLE stocks (date text, symbol text, price real)", database="DUCKDB"
    )
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2021-01-01', 'BOOB', 123.0)", database="DUCKDB"
    )
    job_input.execute_query(
        "CREATE TABLE stocks (date text, symbol text, price real)", database="SQLITE"
    )
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 122.0)", database="SQLITE"
    )
