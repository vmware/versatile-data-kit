# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import datetime
from decimal import Decimal

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    create_table_query = "CREATE TABLE stocks (date text, symbol text, price real)"
    populate_table_query = "INSERT INTO stocks VALUES ('2020-01-01', 'GOOG', 123.0), ('2020-01-01', 'GOOG', 123.0)"
    populate_other_table_query = "INSERT INTO stocks VALUES ('2020-01-01', 'VROOM', 124.0), ('2020-01-01', 'VROOM', 125.0)"
    job_input.execute_query(sql=create_table_query, database="firstdb")
    job_input.execute_query(sql=populate_table_query, database="firstdb")
    job_input.execute_query(sql=create_table_query, database="seconddb")
    job_input.execute_query(sql=populate_other_table_query, database="seconddb")
