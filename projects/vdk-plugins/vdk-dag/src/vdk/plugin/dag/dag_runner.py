# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.dag.api.dag import IDagInput
from vdk.plugin.dag.api.dag import IDagJobStatus
from vdk.plugin.dag.dag import Dag
from vdk.plugin.dag.remote_data_job import JobStatus

TEAM_NAME: Optional[str] = None
DAG_CONFIG = None
JOB_NAME: Optional[str] = None
EXECUTION_ID: Optional[str] = None

log = logging.getLogger(__name__)


def get_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


class DagInput(IDagInput, IDagJobStatus):
    """
    This module is responsible for the execution of DAG of Data Jobs and status checks after the run.
    """

    _running_dag = None  # class variable to hold the DAG instance

    def run_dag(self, jobs: List[Dict]):
        """
        Runs the DAG of jobs - initializes it, builds it, executes it and logs the summary.

        :param jobs: the list of jobs that are part of the DAG
        :return:
        """
        DagInput._running_dag = Dag(TEAM_NAME, DAG_CONFIG, JOB_NAME, EXECUTION_ID)
        DagInput._running_dag.build_dag(jobs)
        DagInput._running_dag.execute_dag()
        log.info(f"DAG summary:\n{DagInput._running_dag}")

    @classmethod
    def get_job_status(cls, job_name: str) -> Optional[JobStatus]:
        """
        Get status of a specified job in the latest DAG execution.
        :return: JobStatus
        """
        if cls._running_dag:
            return cls._running_dag.get_job_status(job_name)
        else:
            log.warning(
                "Job status cannot be checked since there are no registered DAG runs!"
            )
            return None

    @classmethod
    def get_all_jobs_execution_status(cls) -> Optional[Dict[str, JobStatus]]:
        """
        Fetches the statuses of all jobs in the latest DAG execution.

        :return: Dict[str, JobStatus] - A dictionary where keys are job names and values are their statuses.
        """
        if cls._running_dag:
            return cls._running_dag.get_all_jobs_execution_status()
        else:
            log.warning(
                "Job statuses cannot be checked since there are no registered DAG runs!"
            )
            return None

    @classmethod
    def get_jobs_execution_status(
        cls, job_names: List[str]
    ) -> Optional[Dict[str, JobStatus]]:
        """
        Fetches the execution statuses of specified jobs in the latest DAG execution.

        :param job_names: List[str] - A list of job names whose statuses are to be fetched.
        :return: Dict[str, JobStatus] - A dictionary where keys are job names from the input list and values are their
         statuses.
        """
        if cls._running_dag:
            return cls._running_dag.get_jobs_execution_status(job_names)
        else:
            log.warning(
                "Job statuses cannot be checked since there are no registered DAG runs!!"
            )
            return None
