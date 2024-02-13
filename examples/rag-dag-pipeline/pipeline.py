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
                confluence_url="http://confluence.eng.vmware.com/",
                confluence_token=job_input.get_secret("confluence_token"),
                confluence_space_key="TAURUS",
                confluence_parent_page_id="1105807412",
                storage_connection_string=job_input.get_secret(
                    "storage_connection_string"
                ),
            ),
            depends_on=[],
        ),
        dict(
            job_name="pgvector-embedder",
            team_name="Taurus",
            fail_dag_on_error=True,
            arguments=dict(
                destination_metadata_table="vdk_confluence_metadata",
                destination_embeddings_table="vdk_confluence_embeddings",
                storage_connection_string=job_input.get_secret(
                    "storage_connection_string"
                ),
            ),
            depends_on=["confluence-reader"],
        ),
    ]

    DagInput().run_dag(pipeline)
