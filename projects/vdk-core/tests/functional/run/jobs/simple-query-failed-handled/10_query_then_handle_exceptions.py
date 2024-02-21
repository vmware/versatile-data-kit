# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    try:
        job_input.execute_query("SELECT Syntax error")
    except:
        pass  # exception handled by user
