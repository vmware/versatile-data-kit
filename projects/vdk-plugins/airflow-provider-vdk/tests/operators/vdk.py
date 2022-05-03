# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk_provider.operators.vdk import VDKOperator


def test_dummy():
    operator = VDKOperator(
        conn_id="test_conn_id",
        job_name="test_job_name",
        team_name="test_team_name",
        asynchronous=False,
        task_id="test_task_id",
    )

    assert operator
