# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import time
from typing import Dict

from taurus_datajob_api import ApiException
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.meta_jobs.meta import IDataJobExecutor
from vdk.plugin.meta_jobs.meta import TrackableJob
from vdk.plugin.meta_jobs.remote_data_job import JobStatus

log = logging.getLogger(__name__)

ACTIVE_JOB_STATUSES = [JobStatus.SUBMITTED.value, JobStatus.RUNNING.value]


class TrackingDataJobExecutor:
    def __init__(self, executor: IDataJobExecutor):
        self._executor = executor
        self._jobs_cache: Dict[str, TrackableJob] = dict()
        self._time_between_status_check_seconds = int(
            os.environ.get("VDK_META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS", "40")
        )

    def register_job(self, job: TrackableJob):
        if job.job_name in self._jobs_cache:
            log.warning(
                f"Job with name {job.job_name} aleady exists. Details: {self._jobs_cache[job.job_name]}. "
                f"Will overwrite it."
            )
        self._jobs_cache[job.job_name] = job

    def start_job(self, job_name: str) -> None:
        """
        :param job_name: the job to start and track
        """
        job = self.__get_job(job_name)
        job.start_attempt += 1
        execution_id = self._executor.start_job(job.job_name, job.team_name)
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
        job = self.__get_job(job_name)
        details = self._executor.details_job(
            job.job_name, job.team_name, job.execution_id
        )
        job.details = details
        log.info(
            f"Finished data job {job_name}:\n"
            f"start_time: {details['start_time']}\n"
            f"end_time: {details['end_time']}\n"
            f"status: {details['status']}\n"
            f"message: {details['message']}"
        )
        if job.status != JobStatus.SUCCEEDED.value and job.fail_meta_job_on_error:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job failure.",
                    f"Data Job {job_name} failed. See details: {details}",
                    "The rest of the jobs in the meta job will not be started "
                    "and the meta data job will fail.",
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
            )
        return job

    @staticmethod
    def __is_job_submitted(job: TrackableJob):
        return job.status is not None

    def status(self, job_name: str) -> str:
        job = self.__get_job(job_name)
        if job.status in ACTIVE_JOB_STATUSES:
            job.status = self._executor.status_job(
                job.job_name, job.team_name, job.execution_id
            )
        log.debug(f"Job status: {job}")
        return job.status

    def get_finished_job_names(self):
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
        return list(self._jobs_cache.values())

    def get_currently_running_jobs(self):
        return [j for j in self._jobs_cache.values() if j.status in ACTIVE_JOB_STATUSES]
