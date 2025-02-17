# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.plugin.dag.dag_runner import DagInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Dummy arguments {job_input.get_arguments()}")

    job1 = dict(job_name="job1", depends_on=[])
    job2 = dict(job_name="job2", depends_on=["job1"], fail_dag_on_error=False)
    job3 = dict(job_name="job3", depends_on=["job1"])
    job4 = dict(job_name="job4", depends_on=["job2", "job3"])
    DagInput().run_dag([job1, job2, job3, job4])
    job1_status = DagInput().get_job_status(job_name="job1")
    job2_job3_status = DagInput().get_jobs_execution_status(job_names=["job2", "job3"])
    if job1_status:
        log.info(f"Job 1 status was fetched. Status: {job1_status} ")
    if job2_job3_status:
        log.info(f"Job 2 and 3 statuses were fetched. Statuses: {job2_job3_status}")
