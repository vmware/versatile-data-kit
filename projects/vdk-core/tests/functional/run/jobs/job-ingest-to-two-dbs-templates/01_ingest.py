# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    args = {
        "first_db": "duckdb",
        "second_db": "sqlite",
        "first_db_table": "test_duckdb_table",
        "second_db_table": "stocks",
        "first_db_path": os.getenv("DUCKDB_DATABASE"),
        "second_db_path": os.getenv("VDK_SQLITE_FILE"),
    }
    job_input.execute_template("mul-ingest", args)
