# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest import mock
from unittest import TestCase

from taurus_datajob_api import DataJobExecution
from vdk_provider.hooks.vdk import VDKJobExecutionException
from vdk_provider.sensors.vdk import VDKSensor


@mock.patch.dict(
    "os.environ", AIRFLOW_CONN_TEST_CONN_ID="http://https%3A%2F%2Fwww.vdk-endpoint.org"
)
class TestVDKSensor(TestCase):
    def setUp(self):
        self.sensor = VDKSensor(
            conn_id="test_conn_id",
            job_name="test_job_name",
            team_name="test_team_name",
            job_execution_id="test_id",
            task_id="test_task_id",
        )

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_submmitted_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="submitted"
        )

        assert self.sensor.poke(context={}) == False

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_running_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(status="running")

        assert self.sensor.poke(context={}) == False

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_succeeded_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="succeeded"
        )

        assert self.sensor.poke(context={}) == True

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_cancelled_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="cancelled"
        )

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        self.assertEqual(str(e.exception), "Job execution test_id has been cancelled.")

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_skipped_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(status="skipped")

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        self.assertEqual(str(e.exception), "Job execution test_id has been skipped.")

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_user_error_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="user_error"
        )

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        self.assertEqual(
            str(e.exception),
            "Job execution test_id has failed due to a user error. Check job execution logs for more information.",
        )

    @mock.patch("vdk_provider.hooks.vdk.VDKHook.get_job_execution_status")
    def test_platform_error_job_execution(self, mock_get_job_execution_status):
        mock_get_job_execution_status.return_value = DataJobExecution(
            status="platform_error"
        )

        with self.assertRaises(VDKJobExecutionException) as e:
            self.sensor.poke(context={})

        self.assertEqual(
            str(e.exception),
            "Job execution test_id has failed due to a platform error. Check job execution logs for more information.",
        )
