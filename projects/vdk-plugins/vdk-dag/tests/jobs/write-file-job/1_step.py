# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    path = job_input.get_arguments().get("path")
    if path:
        pathlib.Path(path).write_text("data")
