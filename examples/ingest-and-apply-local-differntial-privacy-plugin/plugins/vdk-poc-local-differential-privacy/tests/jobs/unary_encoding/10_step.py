# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    for _ in range(50):
        obj = dict(str_key="str", sensitive_domain="WINDOWS")

        job_input.send_object_for_ingestion(
            payload=obj, destination_table="sample_entity", method="memory"
        )
