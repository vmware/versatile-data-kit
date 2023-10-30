# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.internal.core.logging import bind_logger

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    bound_fields = job_input.get_arguments()["bound_fields"]
    extra_fields = job_input.get_arguments()["extra_fields"]
    bound_logger = bind_logger(
        log,
        bound_fields,
    )

    log.info("Log statement with no bound context")
    bound_logger.info("Log statement with bound context")
    bound_logger.info("Log statement with bound context and extra context", extra=extra_fields)
