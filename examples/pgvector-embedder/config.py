# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os


def get_value(job_input, key: str, default_value=None):
    return job_input.get_arguments().get(
        key, job_input.get_property(key, os.environ.get(key.upper(), default_value))
    )
