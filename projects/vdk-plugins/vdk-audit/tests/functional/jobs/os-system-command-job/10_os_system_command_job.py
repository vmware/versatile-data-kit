# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    os.system("ls")
