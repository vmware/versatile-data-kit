# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
    Read more about conftest.py under: https://pytest.org/latest/plugins.html
"""
import os
from unittest import mock

import pytest


@pytest.fixture(scope="session", autouse=True)
def reduce_retries_in_test_http_requests():
    """
    In order to speed up failures, not wait all re-tries with backoffs (which can be minutes)
    we are reconfiguring the vdk-control-cli to have single retry (1st retry is attempted immediately so no slow down)
    """
    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONTROL_HTTP_READ_RETRIES": "1",
            "VDK_CONTROL_HTTP_CONNECT_RETRIES": "1",
            "VDK_CONTROL_HTTP_TOTAL_RETRIES": "1",
        },
    ) as _fixture:
        yield _fixture
