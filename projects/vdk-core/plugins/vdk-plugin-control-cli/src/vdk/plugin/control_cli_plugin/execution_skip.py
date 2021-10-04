# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import List

from taurus_datajob_api import configuration
from taurus_datajob_api import DataJobExecution
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.termination_message.action import WriteToFileAction
from vdk.internal.builtin_plugins.termination_message.writer_configuration import (
    WriterConfiguration,
)
from vdk.internal.control.auth.auth import Authentication
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.control.rest_lib.factory import ApiClientFactory

log = logging.getLogger(__name__)


class ConcurrentExecutionChecker:
    def __init__(
        self, rest_api_url, api_token, api_token_authorization_url, auth_type
    ) -> None:
        ConcurrentExecutionChecker._authenticate(
            api_token_authorization_url, api_token, auth_type
        )
        self.execution_api_client = ApiClientFactory(rest_api_url).get_execution_api()

    def is_job_execution_running(
        self, job_name, job_team, job_execution_attempt_id
    ) -> bool:
        """
        :param job_name : str value for the job name
        :param job_team : str value for the job team
        :param job_execution_attempt_id : str current job's execution id as returned by VDK execution_state
        This method calls the "/data-jobs/for-team/{team_name}/name/{job_name}/executions"
        endpoint with the additional params "submitted" and "running". The API will return all jobs that are
        submitted and running with the provided team and job name. We have the following possible scenarios:
        API returns an empty list - this means no other data jobs excecutions are running and we can proceed with current execution.
        API returns one execution with a different ID - this means that another excecution is running and we should skip.
        API returns one job with the same ID - this means that we can proceed with excecution.
        API returns two jobs one of which has a different ID - we need to skip current excecution.
        It then parses the response and returns a boolean.
        :return: bool
                 If the data job has a different execution running in K8S.
                 A running different execution means that there is a data job execution currently
                 submitted or running with a different id and in that case we should skip current execution
                 until the other finishes.
        """
        jobs = self._get_running_job_executions(job_name, job_team)
        job_execution_running = False
        for job_execution in jobs:
            # We break only if we have a job with a different execution id
            # Sometimes ids returned by VDK execution_state can slightly differ than
            # ids returned by the API. VDK ids  have '-xxxxx' appended at the end,
            # where x is a random alphameric char. Otherwise ids start the same.
            if not job_execution_attempt_id.startswith(job_execution.id):
                log.info(
                    f"Found another running job execution for {job_name}. Current execution id: {job_execution_attempt_id}. Other running execution id: {job_execution.id}"
                )
                job_execution_running = True
                break

        return job_execution_running

    def _get_running_job_executions(
        self, job_name, team_name
    ) -> List[DataJobExecution]:
        job_status = [
            "submitted",
            "running",
        ]  # We query only for running or manual jobs
        response = self.execution_api_client.data_job_execution_list(
            job_name=job_name, team_name=team_name, execution_status=job_status
        )
        log.info(f"Api call returned job execution list: {response}")
        return response

    @staticmethod
    def _authenticate(api_token_authorization_url, api_token, auth_type) -> None:
        log.info(
            f"Authenticating to check for running data job executions against: {api_token_authorization_url}"
        )
        auth = Authentication()
        auth.update_api_token_authorization_url(api_token_authorization_url)
        auth.update_api_token(api_token)
        auth.update_auth_type(auth_type)
        auth.acquire_and_cache_access_token()
        log.info(
            f"Login successful at: {api_token_authorization_url}, Method: {auth_type}"
        )


def _skip_job_run(job_name) -> None:
    log.info(f"Data job: {job_name} is already running in K8S.")
    log.info(
        f"Skipping execution and exiting. You can retry the job when it finishes executing in K8S."
    )
    os._exit(0)


def _skip_job_if_necessary(
    log_config: str,
    job_name: str,
    execution_id: str,
    job_team: str,
    action: WriteToFileAction,
):
    try:
        log.info("Checking if job should be skipped:")
        log.info(
            f"Job : {job_name}, Team : {job_team}, Log config: {log_config}, execution_id: {execution_id}"
        )
        vdk_config = VDKConfig()
        # vdk_config.
        if log_config != "CLOUD":
            logging.info("Local execution, skipping parallel execution check.")
            return None

        rest_api_url = vdk_config.control_service_rest_api_url
        api_token = vdk_config.api_token
        auth_url = vdk_config.api_token_authorization_server_url
        auth_type = "api-token"

        job_checker = ConcurrentExecutionChecker(
            rest_api_url, api_token, auth_url, auth_type
        )
        job_running = job_checker.is_job_execution_running(
            job_name, job_team, execution_id
        )

        if job_running:
            log.info(f"Skipping job {job_name}")
            action.skipped()
            _skip_job_run(job_name)  # calls os._exit(0)
            return 1  # All other branches return None
    except Exception as exc:
        log.warning(
            f"Error while checking for another data job excecution: {str(exc)} "
        )
        log.warning("Printing stack trace and proceeding with execution:")
        log.warning(exc)
    return None


@hookimpl(tryfirst=True)
def run_job(context: JobContext) -> None:
    try:
        configuration = context.core_context.configuration
        log_config_type = configuration.get_value(vdk_config.LOG_CONFIG)
        job_name = context.name
        job_team = configuration.get_value(JobConfigKeys.TEAM)
        execution_id = configuration.get_value(vdk_config.EXECUTION_ID)
        writer_config = WriterConfiguration(configuration)
        action = WriteToFileAction(writer_config.get_output_file())

        return _skip_job_if_necessary(
            log_config_type, job_name, execution_id, job_team, action
        )
    except Exception as exc:
        log.warning(f"Error while setting up arguments: {str(exc)}")
        log.warning("Catching exception and continuing with execution:")
        log.warning(exc)
        return None
