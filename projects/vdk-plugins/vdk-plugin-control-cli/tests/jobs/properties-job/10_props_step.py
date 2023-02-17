# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    props = job_input.get_all_properties()
    props["new"] = props["original"] + 1
    job_input.set_all_properties(props)
