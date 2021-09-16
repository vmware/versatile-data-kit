# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    # Test creates dynamically file 06_override_properties.py
    # which will override properties

    props = job_input.get_all_properties()
    props["db"] = "memory.default"
    props["table_source"] = "table_source"
    props["table_destination"] = "table_destination"
    props["table_load_destination"] = "table_load_destination"
    job_input.set_all_properties(props)
