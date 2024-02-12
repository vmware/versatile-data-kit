# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    properties = job_input.get_all_properties()
    properties.update(
        dict(
            destination_embeddings_table="vdk_doc_embeddings",
            destination_metadata_table="vdk_doc_metadata",
            chunking_strategy="default",
        )
    )
    job_input.set_all_properties(properties)
