# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import uuid

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    props = job_input.get_all_properties()
    props["id1"] = str(uuid.uuid4())
    props["id2"] = str(uuid.uuid4())
    props["id3"] = str(uuid.uuid4())

    # Test creates dynamically file 06_override_properties.py
    # which will override the following properties
    props["ingest_destination_table"] = "destination_table"
    props["ingest_method"] = "http"
    props["ingest_target"] = "datasource"
    props["ingest_timeout"] = "300"
    props["db"] = "memory.default"
    job_input.set_all_properties(props)
