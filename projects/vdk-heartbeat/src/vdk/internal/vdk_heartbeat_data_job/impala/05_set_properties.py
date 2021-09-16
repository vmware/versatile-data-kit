# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vacloud.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # Test creates dynamically file 06_override_properties.py
    # which will override properties

    props = job_input.get_all_properties()
    props["DATABASE_TEST_DB"] = "dummy"
    job_input.set_all_properties(props)
