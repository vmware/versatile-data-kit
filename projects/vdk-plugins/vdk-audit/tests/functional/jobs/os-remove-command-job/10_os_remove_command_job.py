# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    with open("test_file.txt", "w") as f:
        f.write("Some string")

    os.remove("test_file.txt")
