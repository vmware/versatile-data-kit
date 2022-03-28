# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from airflow.providers.http.hooks.http import HttpHook
from tenacity import sleep
from tenacity import stop_after_attempt
from vdk.internal.builtin_plugins.run.run_status import ExecutionStatus
from vdk.internal.control.auth.auth import Authentication


class VDKHook(HttpHook):
    def __init__(
        self,
        conn_id,
        job_name,
        team_name,
        timeout=1,  # TODO: Set reasonable defaults
        retry_limit=1,
        retry_delay=1,
    ):
        super().__init__(http_conn_id=conn_id)

        self.job_name = job_name
        self.team_name = team_name
        self.timeout = timeout
        self.deployment_id = "production"  # currently multiple deployments are not supported so this remains hardcoded
        # hook methods will use HttpHook's `run_with_advanced_retry` method and pass the _retry_dict as a parameter
        self._retry_dict = {
            "stop": stop_after_attempt(retry_limit),
            "sleep": sleep(retry_delay),
        }
        self.headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {Authentication().read_access_token()}",
        }

    def start_job_execution(self) -> None:
        """
        API path: POST /data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/executions

        """
        pass

    def cancel_job_execution(self, execution_id: str) -> None:
        """
        API path: DELETE /data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}

        :param execution_id: ID of the job execution
        """
        pass

    def get_job_execution_log(self, execution_id: str) -> str:
        """
        API path: GET /data-jobs/for-team/{team_name}/jobs/{job_name}/executions/{execution_id}/logs

        :param execution_id: ID of the job execution
        :return: job execution logs
        """
        pass

    def get_job_execution_status(self, execution_id: str) -> ExecutionStatus:
        """
        API path: GET /data-jobs/for-team/{team_name}/jobs/{job_name}/deployments/{deployment_id}/executions

        :param execution_id: ID of the job execution
        :return: Execution status; either SUCCESS, NOT_RUNNABLE or ERROR
        """
        pass
