# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    obj = dict(
        str_key="str",
        sensitive_key="personal info!!",
    )

    job_input.send_object_for_ingestion(
        payload=obj, destination_table="sample_entity", method="memory"
    )

    obj = dict(
        str_key="str",
        sensitive_key="personal info again!!",
    )

    job_input.send_object_for_ingestion(
        payload=obj, destination_table="sample_entity", method="memory"
    )
