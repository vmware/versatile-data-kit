# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib

from vdk.plugin.test_utils.util_funcs import get_test_job_path


def job_path(job_name: str) -> str:
    return get_test_job_path(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))), job_name
    )
