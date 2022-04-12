# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest import mock

from vdk_provider.sensors.vdk import VDKSensor


@mock.patch.dict(
    "os.environ", AIRFLOW_CONN_TEST_CONN_ID="http://https%3A%2F%2Fwww.vdk-endpoint.org"
)
def test_dummy():
    sensor = VDKSensor(
        conn_id="test_conn_id",
        job_name="test_job_name",
        team_name="test_team_name",
        job_execution_id="test_id",
        task_id="test_task_id",
    )

    assert sensor
