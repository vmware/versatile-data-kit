# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest import mock

import requests_mock
from vdk_provider.hooks.vdk import VDKHook


log = logging.getLogger(__name__)


# Mock the `conn_sample` Airflow connection
@mock.patch.dict(
    "os.environ", AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org"
)
class TestVDKHook(unittest.TestCase):
    @requests_mock.mock()
    def test_start_job_execution(self, m):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/deployments/production/executions"
        # Mock endpoint
        m.post(request_url)

        # Instantiate hook
        hook = VDKHook(conn_id="conn_vdk", job_name="test_job", team_name="test_team")

        hook.start_job_execution()

        assert m.request_history[0].method == "POST"
        assert m.request_history[0].url == request_url

    @requests_mock.mock()
    def test_cancel_job_execution(self, m):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"
        # Mock endpoint
        m.delete(request_url)

        # Instantiate hook
        hook = VDKHook(conn_id="conn_vdk", job_name="test_job", team_name="test_team")

        hook.cancel_job_execution("test_execution_id")

        assert m.request_history[0].method == "DELETE"
        assert m.request_history[0].url == request_url


if __name__ == "__main__":
    unittest.main()
