# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import Mock
from unittest.mock import patch

from taurus_datajob_api import DataJobExecution
from vdk.internal.builtin_plugins.termination_message.action import WriteToFileAction
from vdk.internal.control.rest_lib.factory import DataJobsExecutionApi
from vdk.plugin.control_cli_plugin.execution_skip import _skip_job_if_necessary
from vdk.plugin.control_cli_plugin.execution_skip import ConcurrentExecutionChecker


class ExecutionSkipTest(unittest.TestCase):
    @classmethod
    @patch(
        "vdk.plugin.control_cli_plugin.execution_skip.ConcurrentExecutionChecker._authenticate"
    )
    @patch("vdk.internal.control.rest_lib.factory.ApiClientFactory.__init__")
    @patch("vdk.internal.control.rest_lib.factory.ApiClientFactory.get_execution_api")
    def setUpClass(cls, login_method, api_factory, get_api):
        data_job_1 = Mock(DataJobExecution)
        data_job_1.id = "different_id_string"

        data_job_2 = Mock(DataJobExecution)
        data_job_2.id = "test_id"

        data_job_3 = Mock(DataJobExecution)
        data_job_3.id = "mzhivkov-test-job3-latest-1627588257426-b1027"

        data_job_4 = Mock(DataJobExecution)
        data_job_4.id = "mzhivkov-test-job3-latest-1627583589244-9681d"

        cls.data_job_3_vdk_id = "mzhivkov-test-job3-latest-1627588257426-b1027-2sd5c"
        cls.data_job_4_vdk_id = "mzhivkov-test-job3-latest-1627583589244-9681d-tkr4l"
        cls.data_job_1 = data_job_1
        cls.data_job_2 = data_job_2
        cls.data_job_3 = data_job_3
        cls.data_job_4 = data_job_4

        login_method.return_value = None
        api_factory.return_value = None
        get_api.return_value = None

        cls.checker = ConcurrentExecutionChecker(None, None, None, None)
        cls.mock_api = Mock(DataJobsExecutionApi)
        cls.checker.execution_api_client = cls.mock_api

    def test_api_call_empty_list(self):
        # Behaviour with empty list
        self.mock_api.data_job_execution_list.return_value = []  # Empty list
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", "test_id"
        )
        assert result is False

    def test_api_call_different_id(self):
        # One job with different execution_id
        self.mock_api.data_job_execution_list.return_value = [self.data_job_1]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", "test_id"
        )
        assert result is True

    def test_api_call_similar_incorrect_id(self):
        # One job with incorrect similar id
        self.mock_api.data_job_execution_list.return_value = [self.data_job_3]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", self.data_job_4_vdk_id
        )
        assert result is True

    def test_api_call_same_id(self):
        # One job with same id
        self.mock_api.data_job_execution_list.return_value = [self.data_job_2]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", "test_id"
        )
        assert result is False

    def test_api_call_similar__correct_id(self):
        # One job with correct similar id
        self.mock_api.data_job_execution_list.return_value = [self.data_job_3]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", self.data_job_3_vdk_id
        )
        assert result is False

    def test_api_call_different_ids(self):
        # Two jobs with different ids
        self.mock_api.data_job_execution_list.return_value = [
            self.data_job_1,
            self.data_job_1,
        ]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", "test_id"
        )
        assert result is True

    def test_api_call_similar_different_ids(self):
        # Two jobs similar ids
        self.mock_api.data_job_execution_list.return_value = [
            self.data_job_3,
            self.data_job_3,
        ]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", self.data_job_4_vdk_id
        )
        assert result is True

    def test_api_call_two_jobs(self):
        # Two jobs one matches
        self.mock_api.data_job_execution_list.return_value = [
            self.data_job_1,
            self.data_job_2,
        ]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", "test_id"
        )
        assert result is True

    def test_api_call_two_similar_jobs(self):
        # Two jobs one similar id
        self.mock_api.data_job_execution_list.return_value = [
            self.data_job_3,
            self.data_job_4,
        ]
        result = self.checker.is_job_execution_running(
            "test_job", "test_team", self.data_job_3_vdk_id
        )
        assert result is True

    def test_real_call(self):
        # This test re creates a real DataJobExecution object received from the API as is.
        # Intention is to get as close as possible to the real API call.
        deployment = {
            "deployed_by": "mzhivkov",
            "deployed_date": "datetime.datetime(2021, 7, 29, 18, 8, 55, 435596, tzinfo=tzutc())",
            "enabled": True,
            "id": "release",
            "job_version": "b4d24a249709874ad8c8e43d93ed2824c6ed0292",
            "mode": "release",
            "resources": {
                "cpu_limit": 0.5,
                "cpu_request": 0.5,
                "memory_limit": 1000,
                "memory_request": 1000,
            },
            "schedule": {"schedule_cron": "*/5 * * * *"},
            "vdk_version": "",
        }
        data_job_execution = DataJobExecution(
            "mzhivkov-test-job3-latest-1627583589244-9681d",
            "mzhivkov-test-job3",
            "running",
            "manual",
            "datetime(2021, 7, 29, 18, 33, 9, tzinfo=tzutc())",
            None,
            "manual/vdk-control-cli",
            None,
            "e61d395859dc4c45",
            deployment,
            None,
        )
        self.mock_api.data_job_execution_list.return_value = [data_job_execution]
        result = self.checker.is_job_execution_running(
            "mzhivkov-test-job3",
            "supercollider",
            "mzhivkov-test-job3-latest-1627583589244-9681d-tkr4l",
        )
        assert result == False

    @patch(
        "vdk.plugin.control_cli_plugin.execution_skip.ConcurrentExecutionChecker.is_job_execution_running"
    )
    @patch(
        "vdk.plugin.control_cli_plugin.execution_skip.ConcurrentExecutionChecker._authenticate"
    )
    @patch("vdk.internal.control.rest_lib.factory.ApiClientFactory.__init__")
    @patch("vdk.internal.control.rest_lib.factory.ApiClientFactory.get_execution_api")
    def test_should_skip_method(
        self, login_method, api_factory, get_api, is_job_execution_running
    ):
        # To check SKIPPED status check this to True
        # Beware though as it exits (calls os._exit()) and no results from tests are shown - this is desired behaviour
        is_job_execution_running.return_value = False

        login_method.return_value = None
        api_factory.return_value = None
        get_api.return_value = None
        action = WriteToFileAction("test_skip_file.txt")

        # Check if method executes. Test suceeds if no exception thrown
        _skip_job_if_necessary("CLOUD", "test-job", "test-id", "test-team", action)


if __name__ == "__main__":
    unittest.main()
