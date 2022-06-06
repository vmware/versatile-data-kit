# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator

with DAG(
    "airflow-example",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["example", "vdk"],
) as dag:
    ingest_job1 = VDKOperator(
        conn_id="",
        job_name="ingest_job1",
        team_name="",
        task_id="ingest_job1",
    )

    ingest_job2 = VDKOperator(
        conn_id="",
        job_name="ingest_job2",
        team_name="",
        task_id="ingest_job2",
    )

    transform_job = VDKOperator(
        conn_id="",
        job_name="transform_job",
        team_name="",
        task_id="transform_job",
    )

    [ingest_job1, ingest_job2] >> transform_job
