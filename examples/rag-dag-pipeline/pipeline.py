# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.dag.dag_runner import DagInput


def run(job_input: IJobInput) -> None:
    pipeline = [
        dict(
            job_name="confluence-reader",
            team_name="Taurus",
            fail_dag_on_error=True,
            arguments=dict(
                confluence_url="https://yoansalambashev.atlassian.net/",
                confluence_token="",
                confluence_space_key="RESEARCH",
                # confluence_parent_page_id="1105807412",
            ),
            depends_on=[],
        ),
        dict(
            job_name="chunker",
            team_name="Taurus",
            fail_dag_on_error=True,
            arguments=dict(),
            depends_on=["confluence-reader"],
        ),
        dict(
            job_name="pgvector-embedder",
            team_name="Taurus",
            fail_dag_on_error=True,
            arguments=dict(
                destination_metadata_table="vdk_confluence_metadata_demo_v1",
                destination_embeddings_table="vdk_confluence_embeddings_demo_v1",
            ),
            depends_on=["chunker"],
        ),
    ]

    DagInput().run_dag(pipeline)
