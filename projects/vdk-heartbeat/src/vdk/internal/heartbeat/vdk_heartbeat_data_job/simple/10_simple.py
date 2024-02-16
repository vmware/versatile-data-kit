# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging

from faker import Faker
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # this is just added to test that external libraries are installed and imported correctly from requirements.txt
    fake = Faker()
    log.info(f"Fake name: {fake.name()}")

    log.info(f"Get current properties ")
    props = job_input.get_all_properties()
    props["succeeded"] = "true"
    log.info(f"Save new properties {props}")
    job_input.set_all_properties(props)
    log.info(f"Updated property now to {props['succeeded']}")
