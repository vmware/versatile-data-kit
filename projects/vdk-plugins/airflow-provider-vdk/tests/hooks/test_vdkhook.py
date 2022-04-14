# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
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

        assert mocked_api_client_request.call_args_list[0][0] == ("POST", request_url)

    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_cancel_job_execution(self, mocked_api_client_request):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"

        self.hook.cancel_job_execution("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("DELETE", request_url)

    @mock.patch("taurus_datajob_api.api_client.ApiClient.deserialize")
    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_get_job_execution_status(
        self, mocked_api_client_request, mock_deserialize
    ):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"

        self.hook.get_job_execution_status("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("GET", request_url)

    @mock.patch("taurus_datajob_api.api_client.ApiClient.deserialize")
    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_get_job_execution_log(self, mocked_api_client_request, mock_deserialize):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id/logs"

        self.hook.get_job_execution_log("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("GET", request_url)
