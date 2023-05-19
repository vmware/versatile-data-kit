# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import time
from typing import Dict
from typing import Optional

import urllib3.exceptions as url_exception
from vdk.api.job_input import IJobArguments
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.dag.dags import IDataJobExecutor
from vdk.plugin.dag.dags import TrackableJob
from vdk.plugin.dag.remote_data_job import JobStatus

log = logging.getLogger(__name__)

ACTIVE_JOB_STATUSES = [JobStatus.SUBMITTED.value, JobStatus.RUNNING.value]
SLEEP_TIME = 10
ALLOWED_RETRIES = 3


class TrackingDataJobExecutor:
    """
    The purpose of this class is to execute Data Jobs, track them and change their
    statuses accordingly.
    """

    def __init__(
        self, executor: IDataJobExecutor, time_between_status_check_seconds: int
    ):
        """

        :param executor: the Data Job executor
        :param time_between_status_check_seconds: the number of seconds between status check
        """
        self._executor = executor
        self._jobs_cache: Dict[str, TrackableJob] = dict()
        self._time_between_status_check_seconds = time_between_status_check_seconds

    def register_job(self, job: TrackableJob):
        """
        Registers a Data Job by adding it to the cache.

        :param job: the job to be added to the cache
        :return:
        """
        if job.job_name in self._jobs_cache:
            log.warning(
                f"Job with name {job.job_name} already exists. Details: {self._jobs_cache[job.job_name]}. "
                f"Will overwrite it."
            )
        self._jobs_cache[job.job_name] = job

    def start_job(self, job_name: str) -> None:
        """
        Starts a Data Job.

        :param job_name: the job to start and track
        """
        job = self.__get_job(job_name)
        job.start_attempt += 1
        execution_id = self.start_new_job_execution(
            job_name=job.job_name,
            team_name=job.team_name,
            started_by=job.details.get("started_by"),
            arguments=job.arguments,
        )
        log.info(f"Starting new data job execution with id {execution_id}")
        job.execution_id = execution_id
        job.status = JobStatus.SUBMITTED.value
        job.details = self._executor.details_job(
            job.job_name, job.team_name, job.execution_id
        )
        log.info(
            f"Started data job {job_name}:\n{self.__get_printable_details(job.details)}"
        )

    def finalize_job(self, job_name):
        """
        Finalizes a finished job by updating its details and logging them or raising an error.

        :param job_name: the name of the job
        :return:
        """
        job = self.__get_job(job_name)
        details = self._executor.details_job(
            job.job_name, job.team_name, job.execution_id
        )
        job.details = details
        log.info(
            f"Finished data job {job_name}:\n"
            f"start_time: {details['start_time']}\n"
            f"end_time: {details.get('end_time')}\n"
            f"status: {details['status']}\n"
            f"message: {details['message']}"
        )
        if job.status != JobStatus.SUCCEEDED.value and job.fail_dag_on_error:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "DAG failed due to a Data Job failure.",
                    f"Data Job {job_name} failed. See details: {details}",
                    "The rest of the jobs in the DAG will not be started "
                    "and the DAG will fail.",
                    "Investigate the error in the job or re-try again.",
                )
            )

    @staticmethod
    def __get_printable_details(details):
        del details["deployment"]
        return json.dumps(details, default=lambda o: str(o), indent=2)

    def __get_job(self, job_name) -> TrackableJob:
        job: TrackableJob = self._jobs_cache.get(job_name)
        if job is None:
            raise IndexError(
                f"The job {job_name} has not been registered. Use register_job first. "
                "Alternatively, verify that all of the job names in your job list are spelled correctly."
            )
        return job

    @staticmethod
    def __is_job_submitted(job: TrackableJob):
        return job.status is not None

    def status(self, job_name: str) -> str:
        """
        Gets the status of a job.

        :param job_name: the name of the job
        :return: the job status
        """
        job = self.__get_job(job_name)
        if job.status in ACTIVE_JOB_STATUSES:
            job.status = self._executor.status_job(
                job.job_name, job.team_name, job.execution_id
            )
        log.debug(f"Job status: {job}")
        return job.status

    def execution_type(self, job_name: str, team_name: str, execution_id: str) -> str:
        """
        Gets the execution type of a job.

        :param execution_id: the execution id of the job
        :param team_name: the name of the owning team
        :param job_name: the name of the job
        :return: the job execution type (manual/scheduled)
        """
        details = self._executor.details_job(job_name, team_name, execution_id)
        log.debug(f"Job execution type: {details.get('type')}")
        # the default value for execution type is manual
        return details.get("type", "manual")

    def get_finished_job_names(self):
        """
        :return: list of the names of all the finalized jobs
        """
        finalized_jobs = []
        # TODO: optimize
        # Do not call the status every time (use TTL caching)
        # Do not call all status at the same time - stagger them in time
        # Or use GraphQL API to get status at once (batch)
        for job in self._jobs_cache.values():
            if (
                self.__is_job_submitted(job)
                and job.status in ACTIVE_JOB_STATUSES
                and time.time() - job.last_status_time
                > self._time_between_status_check_seconds
            ):
                job.last_status_time = time.time()
                job.status = self.status(job.job_name)

        for job in self._jobs_cache.values():
            if self.__is_job_submitted(job) and job.status not in ACTIVE_JOB_STATUSES:
                finalized_jobs.append(job.job_name)
        return finalized_jobs

    def get_all_jobs(self):
        """
        :return: list of all jobs
        """
        return list(self._jobs_cache.values())

    def get_currently_running_jobs(self):
        """
        :return: list of jobs with current status SUBMITTED or RUNNING
        """
        return [j for j in self._jobs_cache.values() if j.status in ACTIVE_JOB_STATUSES]

    def start_new_job_execution(
        self,
        job_name: str,
        team_name: str,
        started_by: str = None,
        arguments: IJobArguments = None,
    ) -> str:
        """
        Start a new data job execution.
        The stages of the process are:
            1) Get the latest available execution_id before any new
               executions have been started.
            2) Start a new execution.
            3) In case of a Timeout exception, check if a new execution
               has been started and re-try step 2 if needed.

        NOTE: A loop is used to handle situations, where due to some
        network instability, a socket timeout happens. The execution of
        the data job may have started, but we don't know because an execution
        id was not returned due to the exception.

        :param job_name: name of the data job to be executed
        :param team_name: name of the owning team
        :param started_by: the execution type and the name of the DAG job
        :param arguments: arguments of the data job
        :return: id of the started job execution
        """
        current_retries = 0
        execution_id = None

        latest_available_execution_id = self.get_latest_available_execution_id(
            job_name=job_name, team=team_name
        )

        while current_retries < ALLOWED_RETRIES:
            try:
                execution_id = self._executor.start_job(
                    job_name, team_name, started_by, arguments
                )
                return execution_id
            except url_exception.TimeoutError as e:
                log.info(
                    f"A timeout exception occurred while starting the {job_name} data job. "
                    f"Exception was: {e}"
                )

                execution_id = self.get_latest_available_execution_id(
                    job_name=job_name, team=team_name
                )
                if execution_id and execution_id != latest_available_execution_id:
                    return execution_id
                else:
                    current_retries += 1
                    time.sleep(SLEEP_TIME)  # Sleep for 10 seconds before re-try.

        # If the execution reaches this point, then something has happened,
        # and the state of the data job that has been started cannot be determined.
        raise RuntimeError(
            "Bug, fix me! Something wrong has happened and I cannot recover!"
        )

    def get_latest_available_execution_id(
        self, job_name: str, team: str
    ) -> Optional[str]:
        """
        Get the latest execution_id from the list of all executions for a
        given data job.

        :param job_name: name of data job for which an execution_id is needed
        :param team: name of the team owning the data job
        :return: The execution_id of the latest job execution or None if no
                 executions are available.
        """
        latest_execution_id = None
        executions_list = self._executor.job_executions_list(
            job_name=job_name, team_name=team
        )

        if executions_list:
            # We need only the latest execution which is the last element of the list
            latest_execution_id = executions_list[-1].id
        return latest_execution_id
