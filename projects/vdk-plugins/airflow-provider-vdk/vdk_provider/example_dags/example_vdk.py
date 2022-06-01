# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator

# instantiate the dag
with DAG(
    "example_vdk",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    # run data job example_vdk_job1 belonging to team example_team_name
    job1 = VDKOperator(
        conn_id="example_vdk_connection",
        job_name="example_vdk_job1",
        team_name="example_team_name",
        task_id="job1",
    )

    # run data job example_vdk_job2 belonging to team example_team_name
    job2 = VDKOperator(
        conn_id="example_vdk_connection",
        job_name="example_vdk_job2",
        team_name="team_name",
        task_id="job2",
    )

    # declare job dependencies
    # example_vdk_job1 is executed first, and if it succeeds, example_vdk_job2 is executed
    job1 >> job2
