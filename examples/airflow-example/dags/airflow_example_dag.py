# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator

with DAG(
    "airflow_example_vdk",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["example", "vdk"],
) as dag:
    trino_job1 = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-trino-job1",
        team_name="taurus",
        task_id="trino-job1",
    )

    trino_job2 = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-trino-job2",
        team_name="taurus",
        task_id="trino-job2",
    )

    transform_job = VDKOperator(
        conn_id="vdk-default",
        job_name="airflow-transform-job",
        team_name="taurus",
        task_id="transform-job",
    )

    [trino_job1, trino_job2] >> transform_job
