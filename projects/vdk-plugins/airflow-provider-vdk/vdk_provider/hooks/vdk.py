# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import uuid
from enum import Enum

from airflow.exceptions import AirflowException
from airflow.providers.http.hooks.http import HttpHook
from taurus_datajob_api import ApiClient
from taurus_datajob_api import Configuration
from taurus_datajob_api import DataJobExecution
from taurus_datajob_api import DataJobExecutionRequest
from taurus_datajob_api import DataJobsExecutionApi
from urllib3 import Retry
from vdk.internal.control.auth.auth import Authentication

log = logging.getLogger(__name__)


class VDKJobExecutionException(AirflowException):
    """
    Exception class for exceptions raised for failed, cancelled or skipped job executions.
    """


class JobStatus(str, Enum):
    """
    Enum for the possible statuses a job execution can have.
    """

    SUBMITTED = "submitted"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    USER_ERROR = "user_error"
    PLATFORM_ERROR = "platform_error"


class VDKHook(HttpHook):
    def __init__(
        self,
        conn_id: str,
        job_name: str,
        team_name: str,
        timeout: int = 1,  # TODO: Set reasonable default
    ):
        super().__init__(http_conn_id=conn_id)
        self.job_name = job_name
        self.team_name = team_name
        self.timeout = timeout
        self.deployment_id = "production"  # currently multiple deployments are not supported so this remains hardcoded

        # setting these manually to avoid using VDKConfig
        self.op_id = os.environ.get("VDK_OP_ID_OVERRIDE", f"{uuid.uuid4().hex}"[:16])
        self.http_verify_ssl = os.getenv(
            "VDK_CONTROL_HTTP_VERIFY_SSL", "True"
        ).lower() in ("true", "1", "t")
        self.http_connection_pool_maxsize = int(
            os.getenv("VDK_CONTROL_HTTP_CONNECTION_POOL_MAXSIZE", "2")
        )
        self.http_total_retries = int(os.getenv("VDK_CONTROL_HTTP_TOTAL_RETRIES", "10"))
        self.http_connect_retries = int(
            os.getenv("VDK_CONTROL_HTTP_CONNECT_RETRIES", "6")
        )
        self.http_read_retries = int(os.getenv("VDK_CONTROL_HTTP_READ_RETRIES", "6"))

        self.__execution_api = self._get_execution_api()

    def start_job_execution(self, **request_kwargs) -> None:
        """
        Triggers a manual Datajob execution.

        :param: request_kwargs: Request arguments to be included with the HTTP request
        """
        execution_request = DataJobExecutionRequest(
            started_by="airflow-provider-vdk",
            args=request_kwargs,
        )
        _, _, headers = self.__execution_api.data_job_execution_start_with_http_info(
            team_name=self.team_name,
            job_name=self.job_name,
            deployment_id=self.deployment_id,
            data_job_execution_request=execution_request,
            _request_timeout=self.timeout,
        )
        log.debug(f"Received headers: {headers}")

    def cancel_job_execution(self, execution_id: str) -> None:
        """
        Cancels a Datajob execution.

        :param execution_id: ID of the job execution
        """
        self.__execution_api.data_job_execution_cancel(
            team_name=self.team_name,
            job_name=self.job_name,
            execution_id=execution_id,
            _request_timeout=self.timeout,
        )

    def get_job_execution_log(self, execution_id: str) -> str:
        """
        Returns the stored execution logs for a particular job execution.

        :param execution_id: ID of the job execution
        :return: job execution logs
        """
        return self.__execution_api.data_job_logs_download(
            team_name=self.team_name, job_name=self.job_name, execution_id=execution_id
        ).logs

    def get_job_execution_status(self, execution_id: str) -> DataJobExecution:
        """
        Returns the execution status for a particular job execution.

        :param execution_id: ID of the job execution
        :return: The execution status object listing details about the status of this particular execution
        """
        return self.__execution_api.data_job_execution_read(
            team_name=self.team_name, job_name=self.job_name, execution_id=execution_id
        )

    def _get_rest_api_url_from_connection(self):
        conn = self.get_connection(self.http_conn_id)

        if conn.host and "://" in conn.host:
            base_url = conn.host
        else:
            # schema defaults to HTTPS
            schema = conn.schema if conn.schema else "https"
            host = conn.host if conn.host else ""
            base_url = schema + "://" + host

        if conn.port:
            base_url = base_url + ":" + str(conn.port)

        return base_url

    def _get_execution_api(self):
        rest_api_url = self._get_rest_api_url_from_connection()

        config = Configuration(host=rest_api_url, api_key=None)
        config.connection_pool_maxsize = self.http_connection_pool_maxsize
        config.retries = Retry(
            total=self.http_total_retries,
            connect=self.http_connect_retries,
            read=self.http_read_retries,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
        )
        config.client_side_validation = False
        config.verify_ssl = self.http_verify_ssl

        config.access_token = Authentication().read_access_token()

        api_client = ApiClient(config)
        # We are setting X-OPID - this is send in telemetry and printed in logs on server side - make it easier
        # to troubleshoot and trace requests across different services
        api_client.set_default_header("X-OPID", self.op_id)

        return DataJobsExecutionApi(api_client)
