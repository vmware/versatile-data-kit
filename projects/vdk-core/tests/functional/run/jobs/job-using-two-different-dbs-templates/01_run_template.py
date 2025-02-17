# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    args = {"first_db": "sqlite", "second_db": "duckdb"}
    job_input.execute_template("mul-sql", args)
