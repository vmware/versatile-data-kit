# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import requests
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    target_port = 8783
    while target_port < 65535:
        try:
            response = requests.get(f"http://localhost:{target_port}/threads")
            if response.status_code != 200:
                target_port = target_port + 1
                continue
        except Exception:
            target_port = target_port + 1
            continue
        print(response.status_code)
        print(response.text)

        if "Thread:MainThread" not in response.text:
            raise Exception("unexpected output from server")
        return
    raise Exception("unable to connect to server")
