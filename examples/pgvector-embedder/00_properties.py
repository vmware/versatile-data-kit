# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os.path
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    properties = job_input.get_all_properties()

    output_embeddings = os.path.join("../examples/rag-demo", "embeddings_example.pkl")
    chunks_file = os.path.join("../examples/rag-demo", "chunks_example.json")
    properties.update(
        dict(
            destination_embeddings_table="vdk_confluence_embeddings_demo_v1",
            destination_metadata_table="vdk_confluence_metadata_demo_v1",
            output_embeddings=output_embeddings,
            chunks_file=chunks_file,
        )
    )
    job_input.set_all_properties(properties)
