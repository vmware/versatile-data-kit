# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.plugin.meta_jobs.meta_job_runner import MetaJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Dummy arguments {job_input.get_arguments()}")

    jobs = [
        {"job_name": f"job{i}", "depends_on": [] if i == 1 else ["job1"]}
        for i in range(1, 18)
    ]
    MetaJobInput().run_meta_job(jobs)
