# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os.path
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    properties = job_input.get_all_properties()

    data_file = os.path.join(job_input.get_job_directory(), "documents_example.json")
    output_embeddings = os.path.join(
        job_input.get_temporary_write_directory(), "embeddings_example.pkl"
    )
    properties.update(
        dict(
            destination_embeddings_table="vdk_doc_embeddings",
            destination_metadata_table="vdk_doc_metadata",
            data_file=data_file,
            output_embeddings=output_embeddings,
        )
    )
    job_input.set_all_properties(properties)
