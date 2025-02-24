# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    path = job_input.get_arguments().get("path")
    if path:
        if pathlib.Path(path).read_text() != "data":
            raise ValueError(f"Expected file {path} content to be 'data'")
    else:
        raise ValueError("No path provided.")
