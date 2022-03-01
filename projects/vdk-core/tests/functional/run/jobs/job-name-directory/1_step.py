# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    dir = pathlib.Path(__file__).parent.resolve()
    name = dir.name

    assert job_input.get_name() == name
    assert job_input.get_job_directory() == dir
