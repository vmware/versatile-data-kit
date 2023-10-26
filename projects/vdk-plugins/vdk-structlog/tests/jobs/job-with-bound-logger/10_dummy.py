# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput
from vdk.internal.core.logging import bind_logger

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    bound_logger = bind_logger(log, {'bound_test_key': 'bound_test_value', 'excluded_bound_test_key': 'excluded_value'})

    log.info("Log statement with no bound context")
    bound_logger.info("Log statement with bound context")
    bound_logger.info(
        "Log statement with bound context and extra context",
        extra={'extra_test_key': 'extra_test_value'}
    )
