# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

from vdk.api.job_input import IJobInput


def run(job_input: IJobInput):
    expected_directory_string = job_input.get_arguments()["expected_directory_string"]
    write_directory = job_input.get_write_directory()
    assert str(write_directory) == expected_directory_string
    assert isinstance(write_directory, pathlib.Path)
