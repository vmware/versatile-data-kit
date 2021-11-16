# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    props = job_input.get_all_properties()
    payload = {"id1": props["id1"], "id2": props["id2"], "id3": props["id3"]}

    # Ingest the data
    log.info(f"Sending the following payload for ingestion: {payload}")
    job_input.send_object_for_ingestion(
        payload=payload,
        destination_table=props["ingest_destination_table"],
        method=props["ingest_method"],
        target=props["ingest_target"],
    )
