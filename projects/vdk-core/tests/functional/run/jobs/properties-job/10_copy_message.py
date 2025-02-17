# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    props = job_input.get_all_properties()
    props["message_copy"] = props.get("message")
    job_input.set_all_properties(props)
