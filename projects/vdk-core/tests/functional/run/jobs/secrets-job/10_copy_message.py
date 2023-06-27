# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    secrets = job_input.get_all_secrets()
    secrets["message_copy"] = secrets.get("message")
    job_input.set_all_secrets(secrets)
