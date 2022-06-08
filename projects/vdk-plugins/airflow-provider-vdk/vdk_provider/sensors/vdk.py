# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import Dict

from airflow.sensors.base import BaseSensorOperator
from vdk_provider.hooks.vdk import JobStatus
from vdk_provider.hooks.vdk import VDKHook
from vdk_provider.hooks.vdk import VDKJobExecutionException

log = logging.getLogger(__name__)


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
        **kwargs,
    ):
        super().__init__(
            poke_interval=poke_interval_secs, timeout=timeout_secs, **kwargs
        )
        self.conn_id = conn_id
        self.job_name = job_name
        self.team_name = team_name
        self.job_execution_id = job_execution_id

    def poke(self, context: Dict[Any, Any]) -> bool:
        """
        This method pokes the control-service for the status of a particular job.
        It is executed routinely every `poke_interval_secs` seconds.

        :param context: Airflow context passed through the DAG
        :return: True if some job status condition is met; False otherwise
        """
        vdk_hook = VDKHook(
            conn_id=self.conn_id, job_name=self.job_name, team_name=self.team_name
        )

        job_execution = vdk_hook.get_job_execution_status(self.job_execution_id)
        job_status = job_execution.status

        log.info(
            f"Current status of job execution {self.job_execution_id} is: {job_status}."
        )

        if job_status == JobStatus.SUCCEEDED:
            log.info(f"Job status: {job_execution}")
            log.info(
                f"Job logs: {vdk_hook.get_job_execution_log(self.job_execution_id)}"
            )

            return True
        elif job_status == JobStatus.CANCELLED or job_status == JobStatus.SKIPPED:
            raise VDKJobExecutionException(
                f"Job execution {self.job_execution_id} has been {job_status}."
            )
        elif (
            job_status == JobStatus.USER_ERROR or job_status == JobStatus.PLATFORM_ERROR
        ):
            log.info(
                f"Job logs: {vdk_hook.get_job_execution_log(self.job_execution_id)}"
            )
            raise VDKJobExecutionException(
                f"Job execution {self.job_execution_id} has failed due to a {job_status.replace('_', ' ')}. "
                f"Check the job execution logs above for more information."
            )

        return False
