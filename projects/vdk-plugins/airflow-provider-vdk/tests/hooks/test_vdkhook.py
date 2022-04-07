# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import unittest
from unittest import mock

from vdk_provider.hooks.vdk import VDKHook

log = logging.getLogger(__name__)


class TestVDKHook(unittest.TestCase):
    @mock.patch.dict(
        "os.environ", AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org"
    )
    def setUp(self):
        self.hook = VDKHook(
            conn_id="conn_vdk", job_name="test_job", team_name="test_team"
        )

    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_start_job_execution(self, mocked_api_client_request):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/deployments/production/executions"

        self.hook.start_job_execution()

        mocked_api_client_request.assert_called_with(
            "POST",
            request_url,
            _preload_content=True,
            _request_timeout=1,
            body={"started_by": "airflow-provider-vdk", "args": {}},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": mock.ANY,
                "X-OPID": mock.ANY,
                "Authorization": mock.ANY,
            },
            post_params=[],
            query_params=[],
        )

    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_cancel_job_execution(self, mocked_api_client_request):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"

        self.hook.cancel_job_execution("test_execution_id")

        mocked_api_client_request.assert_called_with(
            "DELETE",
            request_url,
            _preload_content=True,
            _request_timeout=1,
            body=None,
            headers={
                "Accept": "application/json",
                "User-Agent": mock.ANY,
                "X-OPID": mock.ANY,
                "Authorization": mock.ANY,
            },
            post_params=[],
            query_params=[],
        )
