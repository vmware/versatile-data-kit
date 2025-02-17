# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from config import CHUNKS_JSON_FILE
from config import DOCUMENTS_JSON_FILE
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    properties = job_input.get_all_properties()

    data_file = os.path.join(job_input.get_job_directory(), DOCUMENTS_JSON_FILE)
    chunks_file = os.path.join(job_input.get_job_directory(), CHUNKS_JSON_FILE)
    properties.update(
        dict(
            data_file=data_file,
            chunks_file=chunks_file,
            chunking_strategy="fixed",
        )
    )
    job_input.set_all_properties(properties)
