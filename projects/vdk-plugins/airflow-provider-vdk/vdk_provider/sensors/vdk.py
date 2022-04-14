# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import Dict

from airflow.sensors.base import BaseSensorOperator
from vdk_provider.hooks.vdk import VDKHook


class VDKSensor(BaseSensorOperator):
    """
    Sensor which serves to poke an instance of the VDK control-service to check the status of a deployed Data job.

    :param conn_id: ID of the Airflow connection used for the VDKHook
    :param job_name: name of the job which will be poked
    :param team_name: team that the job belongs to
    :param job_execution_id: execution_id of the job execution whose status will be checked
    :param poke_interval_secs: time in seconds in between each individual poke
    :param timeout_secs: time in seconds until the sensor times out
    :param kwargs: extra parameters which will be passed to the BaseSensorOperator superclass
    """

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
        """
        This method pokes the control-service for the status of a particular job.
        It is executed routinely every `poke_interval_secs` seconds.

        :param context: Airflow context passed through the DAG
        :return: True if some job status condition is met; False otherwise
        """
        pass
