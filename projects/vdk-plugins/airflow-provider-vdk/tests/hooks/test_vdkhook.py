# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk_airflow.hooks.vdk import VDKHook


def test_dummy():
    hook = VDKHook("conn_id", "job_name", "team_name")

    assert hook
