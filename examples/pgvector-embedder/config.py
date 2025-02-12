# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os


def get_value(job_input, key: str, default_value=None):
    value = os.environ.get(key.upper(), default_value)
    value = job_input.get_property(key, value)
    value = job_input.get_secret(key, value)
    return job_input.get_arguments().get(key, value)
