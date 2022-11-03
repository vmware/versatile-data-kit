# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Dict

from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.plugin.meta_jobs.meta import IDataJobExecutor
from vdk.plugin.meta_jobs.remote_data_job import RemoteDataJob


class RemoteDataJobExecutor(IDataJobExecutor):
    def start_job(self, job_name: str, team_name: str):
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        return job.start_job_execution()
        # catch error on 409

    def status_job(self, job_name: str, team_name: str, execution_id: str) -> str:
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        status = job.get_job_execution_status(execution_id)
        return status.status

    def details_job(self, job_name: str, team_name: str, execution_id: str) -> dict:
        vdk_cfg = VDKConfig()
        job = RemoteDataJob(job_name, team_name, vdk_cfg.control_service_rest_api_url)
        status = job.get_job_execution_status(execution_id)
        return status.to_dict()
