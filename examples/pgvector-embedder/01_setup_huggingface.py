# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os.path
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    # HF uses temporary directories in the process of its work
    # So make sure to use only allowed ones
    hf_home = job_input.get_temporary_write_directory() / "hf"
    hf_home.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(hf_home)
