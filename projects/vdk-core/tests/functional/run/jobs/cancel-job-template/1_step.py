# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging as log

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    log.info("Step 1.")
    job_input.execute_template("cancel-job", {})
