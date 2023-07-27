# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from faker import Faker
from vacloud.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # this is just added to test that external libraries are installed and imported correctly from requirements.txt
    fake = Faker()
    log.info(f"Fake name: {fake.name()}")

    # Test creates dynamically file 06_override_properties.py
    # which will override properties

    props = job_input.get_all_properties()
    props["DATABASE_TEST_DB"] = "dummy"
    job_input.set_all_properties(props)
