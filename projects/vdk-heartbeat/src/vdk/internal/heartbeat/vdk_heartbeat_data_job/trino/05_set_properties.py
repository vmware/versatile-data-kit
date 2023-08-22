# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from faker import Faker
from vdk.api.job_input import IJobInput


log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # this is just added to test that external libraries are installed and imported correctly from requirements.txt
    fake = Faker()
    log.info(f"Fake name: {fake.name()}")

    # Test creates dynamically file 06_override_properties.py
    # which will override properties

    props = job_input.get_all_properties()
    props["db"] = "memory.default"
    props["table_source"] = "table_source"
    props["table_destination"] = "table_destination"
    props["table_load_destination"] = "table_load_destination"
    job_input.set_all_properties(props)
