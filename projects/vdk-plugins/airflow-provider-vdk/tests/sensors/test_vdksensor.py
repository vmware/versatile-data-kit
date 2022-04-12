# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk_provider.sensors.vdk import VDKSensor


def test_dummy():
    sensor = VDKSensor("test_conn_id", "test_job_name", "test_team_name")

    assert sensor
