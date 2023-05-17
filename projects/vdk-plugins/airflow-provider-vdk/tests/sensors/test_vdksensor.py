# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest import mock
from unittest import TestCase

from taurus_datajob_api import DataJobExecution
from vdk_provider.hooks.vdk import VDKHook
from vdk_provider.hooks.vdk import VDKJobExecutionException
from vdk_provider.sensors.vdk import VDKSensor


class DummyLogsResponse:
    status = 200
    data = b"ddf"
    def getheader(self, str):
        return "json"

@mock.patch.dict(
    "os.environ", AIRFLOW_CONN_TEST_CONN_ID="http://https%3A%2F%2Fwww.vdk-endpoint.org"
)
@mock.patch.object(VDKHook, "_get_access_token", return_value="test1token")
@mock.patch("taurus_datajob_api.api_client.ApiClient.deserialize")
@mock.patch("taurus_datajob_api.api_client.ApiClient.request")
@mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
class TestVDKSensor(TestCase):
    def setUp(self):
        self.sensor = VDKSensor(
            conn_id="test_conn_id",
            job_name="test_job_name",
            team_name="test_team_name",
            job_execution_id="test_id",
            task_id="test_task_id",
        )

    def test_submmitted_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="submitted"
        )

        self.assertEqual(self.sensor.poke(context={}), False)
        mock_access_token.assert_called_once()

    def test_running_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(status="running")

        self.assertEqual(self.sensor.poke(context={}), False)
        mock_access_token.assert_called_once()

    def test_succeeded_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="succeeded"
        )
        mock_request.return_value = DummyLogsResponse()

        self.assertEqual(self.sensor.poke(context={}), True)
        mock_access_token.assert_called_once()

    def test_cancelled_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="cancelled"
        )

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        mock_access_token.assert_called_once()
        self.assertEqual(str(e.exception), "Job execution test_id has been cancelled.")

    def test_skipped_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(status="skipped")

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        mock_access_token.assert_called_once()
        self.assertEqual(str(e.exception), "Job execution test_id has been skipped.")

    def test_user_error_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="user_error"
        )

        mock_request.return_value = DummyLogsResponse()

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        mock_access_token.assert_called_once()
        self.assertEqual(
            str(e.exception),
            "Job execution test_id has failed due to a user error. Check the job execution logs above for more information.",
        )

    def test_platform_error_job_execution(
        self,
        mock_get_job_execution_status,
        mock_request,
        mock_deserialize,
        mock_access_token,
    ):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="platform_error"
        )

        mock_request.return_value = DummyLogsResponse()

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        mock_access_token.assert_called_once()
        self.assertEqual(
            str(e.exception),
            "Job execution test_id has failed due to a platform error. Check the job execution logs above for more information.",
        )
