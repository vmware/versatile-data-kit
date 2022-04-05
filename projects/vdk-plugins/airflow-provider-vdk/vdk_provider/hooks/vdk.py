# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from airflow.providers.http.hooks.http import HttpHook
from taurus_datajob_api import DataJobExecutionRequest
from tenacity import sleep
from tenacity import stop_after_attempt
from vdk.internal.control.auth.auth import Authentication
from vdk.internal.control.rest_lib.factory import ApiClientFactory

log = logging.getLogger(__name__)


class VDKHook(HttpHook):
    def __init__(
        self,
        conn_id: str,
        job_name: str,
        team_name: str,
        timeout: int = 1,  # TODO: Set reasonable default
        retry_limit: int = 3,
        retry_delay: int = 10,
    ):
        super().__init__(http_conn_id=conn_id)
        self.job_name = job_name
        self.team_name = team_name
        self.extra_options = {"timeout": timeout}
        self.deployment_id = "production"  # currently multiple deployments are not supported so this remains hardcoded

        conn = self.get_connection(self.http_conn_id)

        if conn.host and "://" in conn.host:
            self.base_url = conn.host
        else:
            # schema defaults to HTTP
            schema = conn.schema if conn.schema else "http"
            host = conn.host if conn.host else ""
            self.base_url = schema + "://" + host

        if conn.port:
            self.base_url = self.base_url + ":" + str(conn.port)

        self.__execution_api = ApiClientFactory(self.base_url).get_execution_api()

        # hook methods will use HttpHook's `run_with_advanced_retry` method and pass the _retry_dict as a parameter
        # self._retry_dict = {
        #     "stop": stop_after_attempt(retry_limit),
        #     "sleep": sleep(retry_delay),
        # }
        # self.headers = {
        #     "content-type": "application/json",
        #     "authorization": f"Bearer {Authentication().read_access_token()}",
        # }

    def start_job_execution(self, **request_kwargs) -> None:
        """
        Triggers a manual Datajob execution.

        :param: request_kwargs: Request arguments to be included with the HTTP request

        self.method = "POST"
        endpoint = f"/data-jobs/for-team/{self.team_name}/jobs/{self.job_name}/deployments/{self.deployment_id}/executions"

        self.run_with_advanced_retry(
            self._retry_dict,
            endpoint=endpoint,
            headers=self.headers,
            extra_options=self.extra_options,
            json={},
        )
        """
        execution_request = DataJobExecutionRequest(
            started_by=f"vdk-control-cli",
            args=request_kwargs,
        )
        _, _, headers = self.__execution_api.data_job_execution_start_with_http_info(
            team_name=self.team_name,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            data_job_execution_request=execution_request,
        )
        log.debug(f"Received headers: {headers}")

    def cancel_job_execution(self, execution_id: str) -> None:
        """
        Cancels a Datajob execution.

        :param execution_id: ID of the job execution

        self.method = "DELETE"
        endpoint = f"/data-jobs/for-team/{self.team_name}/jobs/{self.job_name}/executions/{execution_id}"

        self.run_with_advanced_retry(
            self._retry_dict,
            endpoint=endpoint,
            headers=self.headers,
            extra_options=self.extra_options,
            json={},
        )
        """
        self.__execution_api.data_job_execution_cancel(
            team_name=self.team_name, job_name=self.job_name, execution_id=execution_id
        )

    def get_job_execution_log(self, execution_id: str) -> str:
        """

        :param execution_id: ID of the job execution
        :return: job execution logs

        self.method = "GET"

        endpoint = f"/data-jobs/for-team/{self.team_name}/jobs/{self.job_name}/executions/{execution_id}/logs"
        return self.run_with_advanced_retry(
            self._retry_dict, endpoint=endpoint, headers=self.headers
        )
        """
        self.method = "DELETE"

        return ""  # included this to ignore faulty codacy check

    def get_job_execution_status(self, execution_id: str):  # -> ExecutionStatus:
        """

        :param execution_id: ID of the job execution
        :return: Execution status; either SUCCESS, NOT_RUNNABLE or ERROR

        self.method = "GET"

        endpoint = f"/data-jobs/for-team/{self.team_name}/jobs/{self.job_name}/deployments/{self.deployment_id}/executions/{execution_id}"
        return self.run_with_advanced_retry(
            self._retry_dict, endpoint=endpoint, data=dict(), headers=self.headers
        )
        """
        self.method = "DELETE"

        return None  # included this to ignore faulty codacy check
