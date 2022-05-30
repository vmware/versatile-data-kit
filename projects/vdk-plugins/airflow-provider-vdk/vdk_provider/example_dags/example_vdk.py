# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator

with DAG(
    "example_vdk",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    op1 = VDKOperator(
        conn_id="example_vdk_connection",
        job_name="example_vdk_job1",
        team_name="team_name",
        task_id="job1",
    )

    op2 = VDKOperator(
        conn_id="tms-example_vdk_connection",
        job_name="gg-example_vdk_job2",
        team_name="team_name",
        task_id="job2",
    )

    op1 >> op2
