# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import asyncio
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info("Test Async step")
    _ = asyncio.Semaphore(2)
