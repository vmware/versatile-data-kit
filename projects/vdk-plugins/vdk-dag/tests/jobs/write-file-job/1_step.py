# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    path = job_input.get_arguments().get("path")
    if path:
        pathlib.Path(path).write_text("data")
