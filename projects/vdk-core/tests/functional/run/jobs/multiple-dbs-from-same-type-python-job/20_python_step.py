# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 122.0)", database="SQLITE"
    )
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2020-01-01', 'VOOV', 122.0)",
        database="first_sqlite",
    )
    job_input.execute_query(
        "INSERT INTO stocks VALUES ('2020-01-01', 'LOOL', 122.0)",
        database="second_sqlite",
    )
