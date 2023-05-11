# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.dag.dag_runner import DagInput


JOBS_RUN_ORDER = [
    {
        "job_name": "ingest-job1",
        "team_name": "my-team",
        "fail_dag_on_error": True,
        "depends_on": [],
    },
    {
        "job_name": "ingest-job2",
        "team_name": "my-team",
        "fail_dag_on_error": True,
        "depends_on": [],
    },
    {
        "job_name": "read-data-job",
        "team_name": "my-team",
        "fail_dag_on_error": True,
        "depends_on": ["ingest-job1", "ingest-job2"],
    },
]


def run(job_input):
    DagInput().run_dag(JOBS_RUN_ORDER)
