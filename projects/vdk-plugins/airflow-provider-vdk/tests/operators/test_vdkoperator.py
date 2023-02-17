# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest import mock
from unittest import TestCase

from taurus_datajob_api import DataJobExecution
from taurus_datajob_api import DataJobExecutionLogs
from vdk_provider.hooks.vdk import VDKHook
from vdk_provider.operators.vdk import VDKOperator


def call_api_return_func(*args, **kwargs):
    if (
        args[0]
        == "/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/executions"
        and args[1] == "POST"
        and args[2]
        == {
            "team_name": "test_team_name",
            "job_name": "test_job_name",
            "deployment_id": "production",
        }
    ):
        return None, None, {"Location": "job-execution-id-01"}
    elif (
        args[0]
        == "/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}"
        and args[1] == "GET"
        and args[2]
        == {
            "team_name": "test_team_name",
            "job_name": "test_job_name",
            "execution_id": "job-execution-id-01",
        }
    ):
        return DataJobExecution(status="succeeded")
    elif (
        args[0]
        == "/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}/logs"
        and args[1] == "GET"
        and args[2]
        == {
            "team_name": "test_team_name",
            "job_name": "test_job_name",
            "execution_id": "job-execution-id-01",
        }
    ):
        return DataJobExecutionLogs(logs="logs")

    return None


@mock.patch.dict(
    "os.environ", AIRFLOW_CONN_CONN_VDK="http://https%3A%2F%2Fwww.vdk-endpoint.org"
)
class TestVDKOperator(TestCase):
    def setUp(self) -> None:
        self.operator = VDKOperator(
            conn_id="conn_vdk",
            job_name="test_job_name",
            team_name="test_team_name",
            asynchronous=False,
            task_id="test_task_id",
        )

    @mock.patch(
        "taurus_datajob_api.ApiClient.call_api", side_effect=call_api_return_func
    )
    @mock.patch.object(VDKHook, "_get_access_token", return_value="test1token")
    def test_execute(self, mock_access_token, mock_call_api):
        self.operator.execute({})

        mock_access_token.assert_called_once()
        assert (
            (
                mock_call_api.call_args_list[0][0][0]
                == "/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/executions"
                and mock_call_api.call_args_list[0][0][1] == "POST"
                and mock_call_api.call_args_list[0][0][2]
                == {
                    "team_name": "test_team_name",
                    "job_name": "test_job_name",
                    "deployment_id": "production",
                }
            )
            and (
                mock_call_api.call_args_list[1][0][0]
                == "/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}"
                and mock_call_api.call_args_list[1][0][1] == "GET"
                and mock_call_api.call_args_list[1][0][2]
                == {
                    "team_name": "test_team_name",
                    "job_name": "test_job_name",
                    "execution_id": "job-execution-id-01",
                }
            )
            and (
                mock_call_api.call_args_list[2][0][0]
                == "/data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}/logs"
                and mock_call_api.call_args_list[2][0][1] == "GET"
                and mock_call_api.call_args_list[2][0][2]
                == {
                    "team_name": "test_team_name",
                    "job_name": "test_job_name",
                    "execution_id": "job-execution-id-01",
                }
            )
        )
