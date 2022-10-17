# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
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

    def register_job(self, job: TrackableJob):
        if job.job_name in self._jobs_cache:
            log.warning(
                f"Job with name {job.job_name} aleady exists. Details: {self._jobs_cache[job.job_name]}. "
                f"Will overwrite it."
            )
        self._jobs_cache[job.job_name] = job

    def start_job(self, job_name: str) -> None:
        """
        :param job: the job to start and track
        """
        job = self._get_job(job_name)
        try:
            execution_id = self._executor.start_job(job.job_name, job.team_name)
            log.info(f"Starting new data job execution with id {execution_id}")
            self._jobs_cache[job.job_name] = job
            job.execution_id = execution_id
            job.status = JobStatus.SUBMITTED.value
            details = self._executor.details_job(
                job.job_name, job.team_name, job.execution_id
            )
            job.details = details
            log.info(
                f"Started data job {job_name}:\n{self._get_printable_details(details)}"
            )
        except ApiException as e:
            if e.status == 409:
                log.info(f"Detected conflict with another runnig job: {e}")

    def finalize_job(self, job_name):
        job = self._get_job(job_name)
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
    def _get_printable_details(details):
        del details["deployment"]
        return json.dumps(details, default=lambda o: str(o), indent=2)

    def _get_job(self, job_name) -> TrackableJob:
        job: TrackableJob = self._jobs_cache.get(job_name)
        if job is None:
            raise IndexError(
                f"The job {job_name} has not been registered. Use register_job first. "
            )
        return job

    def status(self, job_name: str) -> str:
        job = self._get_job(job_name)
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
        for job in self._jobs_cache.values():
            if job.status is not None and job.status in ACTIVE_JOB_STATUSES:
                job.status = self.status(job.job_name)

        for job in self._jobs_cache.values():
            if job.status is not None and job.status not in ACTIVE_JOB_STATUSES:
                finalized_jobs.append(job.job_name)
        return finalized_jobs

    def get_all_jobs(self):
        return list(self._jobs_cache.values())
