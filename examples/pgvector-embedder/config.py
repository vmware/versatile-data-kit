# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os


def get_value(job_input, key: str, default_value=None):
    value = os.environ.get(key.upper(), default_value)
    value = job_input.get_property(key, value)
    value = job_input.get_secret(key, value)
    return job_input.get_arguments().get(key, value)
