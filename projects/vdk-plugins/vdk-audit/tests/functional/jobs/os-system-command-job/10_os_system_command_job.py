# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    os.system("ls")
