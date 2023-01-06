# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import requests
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    response = requests.get("http://localhost:8783/threads")
    print(response.status_code)
    print(response.text)

    if response.status_code != 200:
        raise Exception("unexpected response code from server")

    if "Thread:MainThread" not in response.text:
        raise Exception("unexpected output from server")
