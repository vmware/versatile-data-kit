# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    args = dict()
    try:
        job_input.execute_template("csv-risky", args)
    except pd.errors.EmptyDataError as e:
        log.info("Handling empty data error")
        log.exception(e)
