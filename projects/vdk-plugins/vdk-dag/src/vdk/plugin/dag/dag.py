# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pprint
import sys
import time
from graphlib import TopologicalSorter
from typing import Any
from typing import Dict
from typing import List

from taurus_datajob_api import ApiException
from vdk.plugin.dag.cached_data_job_executor import TrackingDataJobExecutor
from vdk.plugin.dag.dag_plugin_configuration import DagPluginConfiguration
from vdk.plugin.dag.dag_validator import DagValidator
from vdk.plugin.dag.dags import TrackableJob
from vdk.plugin.dag.remote_data_job_executor import RemoteDataJobExecutor
from vdk.plugin.dag.time_based_queue import TimeBasedQueue

log = logging.getLogger(__name__)


class Dag:
    def __init__(
        self,
        team_name: str,
        dags_config: DagPluginConfiguration,
        job_name: str = None,
        execution_id: str = None,
    ):
        """
        This module deals with all the DAG-related operations such as build and execute.

        :param team_name: the name of the owning team
        :param dags_config: the DAG job configuration
        """
        self._team_name = team_name
        self._topological_sorter = TopologicalSorter()
        self._delayed_starting_jobs = TimeBasedQueue(
            min_ready_time_seconds=dags_config.dags_delayed_jobs_min_delay_seconds(),
            randomize_delay_seconds=dags_config.dags_delayed_jobs_randomized_added_delay_seconds(),
        )
        self._max_concurrent_running_jobs = (
            dags_config.dags_max_concurrent_running_jobs()
        )
        self._finished_jobs = []
        self._dag_execution_check_time_period_seconds = (
            dags_config.dags_dag_execution_check_time_period_seconds()
        )
        self._job_executor = TrackingDataJobExecutor(
            executor=RemoteDataJobExecutor(),
            time_between_status_check_seconds=dags_config.dags_time_between_status_check_seconds(),
        )
        self._dag_validator = DagValidator()
        if job_name is not None:
            if execution_id is not None:
                try:
                    self._started_by = (
                        self._job_executor.execution_type(
                            job_name, team_name, execution_id
                        )
                        + "/"
                        + job_name
                    )
                except ApiException as e:
                    if e.status == 404:
                        log.debug(
                            f"Job {job_name} of team {team_name} with execution id {execution_id} failed. "
                            f"Local job runs return 404 status when getting the execution type: {e}"
                        )
                    else:
                        log.info(
                            f"Unexpected error while checking for job execution type for job {job_name} "
                            f"with execution id {execution_id} of team {team_name}: {e}"
                        )
                    self._started_by = f"manual/{job_name}"
            else:
                self._started_by = f"manual/{job_name}"
        else:
            self._started_by = "manual/default"

    def build_dag(self, jobs: List[Dict]):
        """
        Validate the jobs and build a DAG based on their dependency lists.

        :param jobs: the jobs that are part of the DAG
        :return:
        """
        self._dag_validator.validate(jobs)
        for job in jobs:
            trackable_job = TrackableJob(
                job["job_name"],
                job.get("team_name", self._team_name),
                job.get("fail_dag_on_error", True),
                job.get("arguments", None),
                job.get("details", {}),
            )
            trackable_job.details = {"started_by": self._started_by}
            self._job_executor.register_job(trackable_job)
            self._topological_sorter.add(trackable_job.job_name, *job["depends_on"])

    def execute_dag(self):
        """
        Execute the DAG of jobs.

        :return:
        """
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
