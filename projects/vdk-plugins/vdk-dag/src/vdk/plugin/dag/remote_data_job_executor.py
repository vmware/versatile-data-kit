# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import List
from typing import Optional

from taurus_datajob_api import DataJobExecution
from vdk.api.job_input import IJobArguments
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.plugin.dag.dags import IDataJobExecutor
from vdk.plugin.dag.remote_data_job import RemoteDataJob


class RemoteDataJobExecutor(IDataJobExecutor):
    """
    This module is responsible for executing remote Data Jobs.
    """

    def start_job(
        self,
        job_name: str,
        team_name: str,
        started_by: str = None,
        arguments: IJobArguments = None,
    ):
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(
            job_name,
            team_name,
            vdk_cfg.control_service_rest_api_url,
            started_by,
            arguments,
        )
        return job.start_job_execution()
        # catch error on 409

    def status_job(self, job_name: str, team_name: str, execution_id: str) -> str:
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        details = job.get_job_execution_details(execution_id)
        return details.status

    def details_job(self, job_name: str, team_name: str, execution_id: str) -> dict:
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        details = job.get_job_execution_details(execution_id)
        return details.to_dict()

    def job_executions_list(
        self, job_name: str, team_name: str
    ) -> Optional[List[DataJobExecution]]:
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        executions_list = job.get_job_executions()
        return executions_list
