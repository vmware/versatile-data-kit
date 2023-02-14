# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import unittest
from unittest import mock

from vdk.plugin.control_api_auth.authentication import Authentication
from vdk_provider.hooks.vdk import VDKHook

log = logging.getLogger(__name__)


# Monkey-patch the authentication logic to allow for more granular testing
# of the VDKHook
class PatchedAuth(Authentication):
    def read_access_token(self) -> str:
        return "test1token"


class TestVDKHook(unittest.TestCase):
    @mock.patch.dict(
        "os.environ", AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org"
    )
    def setUp(self):
        self.hook = VDKHook(
            conn_id="conn_vdk",
            job_name="test_job",
            team_name="test_team",
            auth=PatchedAuth(),
        )

    @mock.patch("taurus_datajob_api.api_client.ApiClient.call_api")
    def test_start_job_execution(self, mock_call_api):
        mock_call_api.return_value = (None, None, {"Location": "job-execution-id-01"})

        self.hook.start_job_execution()

        assert (
            mock_call_api.call_args_list[0][0][0]
            == "/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/executions"
            and mock_call_api.call_args_list[0][0][1] == "POST"
            and mock_call_api.call_args_list[0][0][2]
            == {
                "team_name": "test_team",
                "job_name": "test_job",
                "deployment_id": "production",
            }
        )

    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_cancel_job_execution(self, mocked_api_client_request):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"

        self.hook.cancel_job_execution("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("DELETE", request_url)

    @mock.patch("taurus_datajob_api.api_client.ApiClient.deserialize")
    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_get_job_execution_status(self, mocked_api_client_request, _):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id"

        self.hook.get_job_execution_status("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("GET", request_url)

    @mock.patch("taurus_datajob_api.api_client.ApiClient.deserialize")
    @mock.patch("taurus_datajob_api.api_client.ApiClient.request")
    def test_get_job_execution_log(self, mocked_api_client_request, _):
        request_url = "https://www.vdk-endpoint.org/data-jobs/for-team/test_team/jobs/test_job/executions/test_execution_id/logs"

        self.hook.get_job_execution_log("test_execution_id")

        assert mocked_api_client_request.call_args_list[0][0] == ("GET", request_url)
