# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from airflow import DAG
from vdk_provider.operators.vdk import VDKOperator
from vdk_provider.sensors.vdk import VDKSensor

# instantiate the DAG; the structure looks like this:
# DAG:  - job1
#       - job1_sensor >> job2
# This means that job1 and job1_sensor start simultaneously, and if the sensor
# confirms job1 is successful, job2 starts
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
        asynchronous=True,
        task_id="job1",
    )

    job1_sensor = VDKSensor(
        conn_id="example_vdk_connection",
        job_name="example_vdk_job1",
        team_name="example_team_name",
        job_execution_id=job1.output,
        task_id="job1_sensor",
    )

    # run data job example_vdk_job2 belonging to team example_team_name
    job2 = VDKOperator(
        conn_id="example_vdk_connection",
        job_name="example_vdk_job2",
        team_name="team_name",
        task_id="job2",
    )

    # declare job dependencies
    # example_vdk_job1 is executed first; then, the corresponding sensor pings the control-service periodically
    # until the job execution completes and if it is successful, example_vdk_job2 is executed
    job1_sensor >> job2
