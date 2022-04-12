# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import Dict

from airflow.sensors.base import BaseSensorOperator
from vdk_provider.hooks.vdk import VDKHook


class VDKSensor(BaseSensorOperator):
    def __init__(
        self,
        conn_id: str,
        job_name: str,
        team_name: str,
        job_execution_id: str,
        poke_interval_secs: int = 30,
        timeout_secs: int = 24 * 60 * 60,
        **kwargs
    ):
        super().__init__(
            poke_interval=poke_interval_secs, timeout=timeout_secs, **kwargs
        )
        self.job_execution_id = job_execution_id

        self.hook = VDKHook(conn_id, job_name, team_name)

    def poke(self, context: Dict[Any, Any]) -> bool:
        pass
