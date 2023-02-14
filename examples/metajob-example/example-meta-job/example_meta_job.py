# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.meta_jobs.meta_job_runner import MetaJobInput


JOBS_RUN_ORDER = [
    {
        "job_name": "ingest-job1",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "depends_on": [],
    },
    {
        "job_name": "ingest-job2",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "depends_on": [],
    },
    {
        "job_name": "read-data-job",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "depends_on": ["ingest-job1", "ingest-job2"],
    },
]


def run(job_input):
    MetaJobInput().run_meta_job(JOBS_RUN_ORDER)
