# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.plugin.dag.dag_runner import DagInput

# ELT

jobs = [
    dict(
        job_name="confluence-reader",
        team_name="my-team",
        fail_dag_on_error=True,
        arguments=dict(data_file=f"/tmp/confluence.json"),
        depends_on=[],
    ),
    dict(
        job_name="pgvector-embedder",
        team_name="my-team",
        fail_dag_on_error=True,
        arguments=dict(
            data_file=f"/tmp/confluence.json",
            destination_metadata_table="vdk_confluence_metadata",
            destination_embeddings_table="vdk_confluence_embeddings",
        ),
        depends_on=["confluence-reader"],
    ),
]


def run(job_input) -> None:
    DagInput().run_dag(jobs)
