# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    job_directory = pathlib.Path(__file__).parent.resolve()
    name = job_directory.name

    assert job_input.get_name() == name
    assert job_input.get_job_directory() == job_directory
