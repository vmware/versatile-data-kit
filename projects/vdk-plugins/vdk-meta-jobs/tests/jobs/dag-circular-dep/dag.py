# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.plugin.dags.dag_runner import DAGInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Dummy arguments {job_input.get_arguments()}")

    # circular dependency:
    # job2 depends on job4 which depends on job3 which depends on job2
    job1 = dict(job_name="job1", depends_on=[])
    job2 = dict(job_name="job2", depends_on=["job1", "job4"])
    job3 = dict(job_name="job3", depends_on=["job1", "job2"])
    job4 = dict(job_name="job4", depends_on=["job3"])
    DAGInput().run_dag([job1, job2, job3, job4])
