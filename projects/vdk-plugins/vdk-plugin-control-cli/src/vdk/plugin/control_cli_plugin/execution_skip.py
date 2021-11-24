# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import List

from taurus_datajob_api import DataJobExecution
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.termination_message.writer import (
    TerminationMessageWriterPlugin,
)
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.statestore import CommonStoreKeys

log = logging.getLogger(__name__)
EXECUTION_SKIP_CHECKER_ENABLED = "EXECUTION_SKIP_CHECKER_ENABLED"


class ConcurrentExecutionChecker:
    """
    The class make sure to check if there is another execution of the data job already started.
    It is used to prevent concurrent executions from getting started in the same time.
    As often data jobs are not expected to be parallelizable since they do maintain state - for example
    ingestion job that pulls data since last time it ran and moves it to a warehouse would duplicate it
    if started concurrently.
    """

    def __init__(self, rest_api_url: str) -> None:
        # set as protected instead of private so it can be mocked in unit tests
        self._execution_api_client = ApiClientFactory(rest_api_url).get_execution_api()

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
        response = self._execution_api_client.data_job_execution_list(
            job_name=job_name, team_name=team_name, execution_status=job_status
        )
        log.info(f"Api call returned job execution list: {response}")
        return response


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
    configuration: Configuration,
):
    try:
        log.info("Checking if job should be skipped:")
        log.info(
            f"Job : {job_name}, Team : {job_team}, Log config: {log_config}, execution_id: {execution_id}"
        )
        # TODO: Do not use log config type to check if it is a cloud run or not.
        if log_config != "CLOUD":
            logging.info("Local execution, skipping parallel execution check.")
            return None

        vdk_cfg = VDKConfig()
        job_checker = ConcurrentExecutionChecker(vdk_cfg.control_service_rest_api_url)
        job_running = job_checker.is_job_execution_running(
            job_name, job_team, execution_id
        )

        if job_running:
            log.info(f"Skipping job {job_name}")
            writer_plugin = TerminationMessageWriterPlugin()
            writer_plugin.write_termination_message(
                configuration=configuration, execution_skipped=True
            )
            _skip_job_run(job_name)  # calls os._exit(0)
            return 1  # All other branches return None
    except Exception as exc:
        log.warning(
            f"Error while checking for another data job excecution: {str(exc)} "
        )
        log.warning("Printing stack trace and proceeding with execution:")
    return None


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=EXECUTION_SKIP_CHECKER_ENABLED,
        default_value=True,
        description="Set to false if you want to disable execution skipping logic entirely.",
    )


@hookimpl(tryfirst=True)
def run_job(context: JobContext) -> None:
    try:
        configuration = context.core_context.configuration

        if not configuration.get_value(EXECUTION_SKIP_CHECKER_ENABLED):
            log.info(
                "Skipping logic is turned off. Continuing with current execution without checking for another running execution."
            )
            return None

        log_config_type = configuration.get_value(vdk_config.LOG_CONFIG)
        job_name = context.name
        job_team = configuration.get_value(JobConfigKeys.TEAM)
        execution_id = context.core_context.state.get(CommonStoreKeys.EXECUTION_ID)

        return _skip_job_if_necessary(
            log_config_type, job_name, execution_id, job_team, configuration
        )
    except Exception as exc:
        log.warning(f"Error while setting up arguments: {str(exc)}")
        log.warning("Catching exception and continuing with execution:")
        log.warning(exc)
        return None
