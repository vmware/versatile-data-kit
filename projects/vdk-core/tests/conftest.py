# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
    Dummy conftest.py for vdk-core.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
# import pytest
from tenacity import wait_none
from vdk.internal.builtin_plugins.connection.managed_connection_base import (
    ManagedConnectionBase,
)

# reduce wait time to 0 between tenacity re-tries during tests to speed up failures
ManagedConnectionBase.connect.retry.wait = wait_none()
