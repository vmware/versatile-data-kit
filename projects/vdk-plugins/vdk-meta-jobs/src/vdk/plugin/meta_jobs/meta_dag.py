# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import pprint
import sys
import time
from graphlib import TopologicalSorter
from typing import Any
from typing import Dict
from typing import List

from taurus_datajob_api import ApiException
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import UserCodeError
from vdk.plugin.meta_jobs.cached_data_job_executor import TrackingDataJobExecutor
from vdk.plugin.meta_jobs.meta import TrackableJob
from vdk.plugin.meta_jobs.meta_configuration import MetaPluginConfiguration
from vdk.plugin.meta_jobs.remote_data_job_executor import RemoteDataJobExecutor
from vdk.plugin.meta_jobs.time_based_queue import TimeBasedQueue

log = logging.getLogger(__name__)


class MetaJobsDag:
    def __init__(self, team_name: str, meta_config: MetaPluginConfiguration):
        self._team_name = team_name
        self._topological_sorter = TopologicalSorter()
        self._delayed_starting_jobs = TimeBasedQueue(
            min_ready_time_seconds=meta_config.meta_jobs_delayed_jobs_min_delay_seconds(),
            randomize_delay_seconds=meta_config.meta_jobs_delayed_jobs_randomized_added_delay_seconds(),
        )
        self._max_concurrent_running_jobs = (
            meta_config.meta_jobs_max_concurrent_running_jobs()
        )
        self._finished_jobs = []
        self._dag_execution_check_time_period_seconds = (
            meta_config.meta_jobs_dag_execution_check_time_period_seconds()
        )
        self._job_executor = TrackingDataJobExecutor(
            executor=RemoteDataJobExecutor(),
            time_between_status_check_seconds=meta_config.meta_jobs_time_between_status_check_seconds(),
        )

    def build_dag(self, jobs: List[Dict]):
        for job in jobs:
            self._validate_job(job)
            trackable_job = TrackableJob(
                job["job_name"],
                job.get("team_name", self._team_name),
                job.get("fail_meta_job_on_error", True),
            )
            self._job_executor.register_job(trackable_job)
            self._topological_sorter.add(trackable_job.job_name, *job["depends_on"])

    def execute_dag(self):
        self._topological_sorter.prepare()
        while self._topological_sorter.is_active():
            for node in self._topological_sorter.get_ready():
                self._start_job(node)
            self._start_delayed_jobs()
            finished_jobs = self._get_finished_jobs()
            self._finalize_jobs(finished_jobs)
            if not finished_jobs:
                # No jobs are finished at this iteration so let's wait a bit to let them
                # finish
                time.sleep(self._dag_execution_check_time_period_seconds)

    def _get_finished_jobs(self):
        return [
            job
            for job in self._job_executor.get_finished_job_names()
            if job not in self._finished_jobs
        ]

    def _finalize_jobs(self, finalized_jobs):
        for node in finalized_jobs:
            log.info(f"Data Job {node} has finished.")
            self._topological_sorter.done(node)
            self._job_executor.finalize_job(node)
            self._finished_jobs.append(node)

    def _start_delayed_jobs(self):
        while (
            len(self._job_executor.get_currently_running_jobs())
            < self._max_concurrent_running_jobs
        ):
            job = self._delayed_starting_jobs.dequeue()
            if job is None:
                break
            log.info(f"Trying to start job {job} again.")
            self._start_job(job)

    def __repr__(self):
        # TODO move out of this class
        def default_serialization(o: Any) -> Any:
            return o.__dict__ if "__dict__" in dir(o) else str(o)

        jobs = self._job_executor.get_all_jobs()
        data = [j.details if j.details is not None else j.__dict__ for j in jobs]
        try:
            result = json.dumps(data, default=default_serialization, indent=2)
        except Exception as e:
            log.debug(f"Failed to json.dumps : {e}. Fallback to pprint.")
            # sort_dicts is supported since 3.8
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
                result = pprint.pformat(
                    data, indent=2, depth=5, compact=False, sort_dicts=False
                )
            else:
                result = pprint.pformat(data, indent=2, depth=5, compact=False)
        return result

    def _start_job(self, node):
        try:
            curr_running_jobs = len(self._job_executor.get_currently_running_jobs())
            if curr_running_jobs >= self._max_concurrent_running_jobs:
                log.info(
                    f"Starting job {node} fail - too many concurrently running jobs. Currently running: "
                    f"{curr_running_jobs}, limit: {self._max_concurrent_running_jobs}. Will be re-tried later"
                )
                self._delayed_starting_jobs.enqueue(node)
            else:
                self._job_executor.start_job(node)
        except ApiException as e:
            if e.status == 409:
                log.info(
                    f"Detected conflict with another running job: {e}. Will be re-tried later"
                )
                self._delayed_starting_jobs.enqueue(node)
            elif e.status >= 500:
                log.info(
                    f"Starting job fail with server error : {e}. Will be re-tried later"
                )
                self._delayed_starting_jobs.enqueue(node)
            else:
                raise

    def _validate_job(self, job: Dict):
        allowed_job_keys = [
            "job_name",
            "team_name",
            "fail_meta_job_on_error",
            "depends_on",
        ]
        required_job_keys = ["job_name", "depends_on"]
        registered_job_names = [j.job_name for j in self._job_executor.get_all_jobs()]
        if type(job) != dict:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job failed. "
                    f"There is an error with the type of job name.",
                    "The DAG will not be built and the meta data job will fail.",
                    f"Check the Data Job type. Expected type is dict.",
                )
            )
        if any(key not in allowed_job_keys for key in job.keys()) or any(
            key not in job for key in required_job_keys
        ):
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job failed. "
                    "Some keys in the Data Job Dict are not allowed or some of the required ones are missing.",
                    "The DAG will not be built and the Meta Job will fail.",
                    "Check the Data Job Dict keys for errors and make sure the required ones are present.",
                )
            )
        if type(job["job_name"]) != str:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job failed. "
                    f"There is an error with the type of job name.",
                    "The DAG will not be built and the Meta Job will fail.",
                    f"Check the Data Job Dict value of job_name. Expected type is string.",
                )
            )
        if job["job_name"] in registered_job_names:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job {job['job_name']} failed. "
                    f"Job with such name already exists.",
                    "The DAG will not be built and the Meta Job will fail.",
                    "Check the Data Job Dict value of job_name.",
                )
            )
        if not (
            isinstance(job["depends_on"], list)
            and all(isinstance(pred, str) for pred in job["depends_on"])
        ):
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job {job['job_name']} failed. "
                    f"There is an error with the type of the depends_on value.",
                    "The DAG will not be built and the Meta Job will fail.",
                    "Check the Data Job Dict value of depends_on. Expected type is list of strings.",
                )
            )
        if any(pred not in registered_job_names for pred in job["depends_on"]):
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job {job['job_name']} failed. "
                    f"There is an error with the dependencies {job['depends_on']}.",
                    "The DAG will not be built and the Meta Job will fail.",
                    "Check the Data Job Dict dependencies.",
                )
            )
        if "team_name" in job and type(job["team_name"]) != str:
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job {job['job_name']} failed. "
                    f"There is an error with the type of team name.",
                    "The DAG will not be built and the Meta Job will fail.",
                    f"Check the Data Job Dict value of team_name. Expected type is string.",
                )
            )
        if (
            "fail_meta_job_on_error" in job
            and type(job["fail_meta_job_on_error"]) != bool
        ):
            raise UserCodeError(
                ErrorMessage(
                    "",
                    "Meta Job failed due to a data job validation failure.",
                    f"Validation of Data Job {job['job_name']} failed. "
                    f"There is an error with the type of the fail_meta_job_on_error option.",
                    "The DAG will not be built and the Meta Job will fail.",
                    "Check the Data Job Dict value of fail_meta_job_on_error. Expected type is bool.",
                )
            )
        log.info(f"Successfully validated job: {job['job_name']}")
