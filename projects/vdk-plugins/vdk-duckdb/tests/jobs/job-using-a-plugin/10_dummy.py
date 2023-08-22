# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    log.info(f"Dummy arguments {job_input.get_arguments()}")

    # job_input.execute_query("some duckdb")
