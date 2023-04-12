# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.meta_jobs.meta_job_runner import MetaJobInput

JOBS_RUN_ORDER = [
    {
        "job_name": "ingest-job-table-one",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "arguments": {
            "db_table": "test_dag_one",
            "db_schema": "default",
            "db_catalog": "memory",
        },
        "depends_on": [],
    },
    {
        "job_name": "ingest-job-table-two",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "arguments": {
            "db_table": "test_dag_two",
            "db_schema": "default",
            "db_catalog": "memory",
        },
        "depends_on": [],
    },
    {
        "job_name": "read-job-usa",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "arguments": {
            "db_tables": ["test_dag_one", "test_dag_two"],
            "db_schema": "default",
            "db_catalog": "memory",
        },
        "depends_on": ["ingest-job-table-one", "ingest-job-table-two"],
    },
    {
        "job_name": "read-job-canada",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "arguments": {
            "db_tables": ["test_dag_one", "test_dag_two"],
            "db_schema": "default",
            "db_catalog": "memory",
        },
        "depends_on": ["ingest-job-table-one", "ingest-job-table-two"],
    },
    {
        "job_name": "read-job-rest-of-world",
        "team_name": "my-team",
        "fail_meta_job_on_error": True,
        "arguments": {
            "db_tables": ["test_dag_one", "test_dag_two"],
            "db_schema": "default",
            "db_catalog": "memory",
        },
        "depends_on": ["ingest-job-table-one", "ingest-job-table-two"],
    },
]


def run(job_input):
    MetaJobInput().run_meta_job(JOBS_RUN_ORDER)
