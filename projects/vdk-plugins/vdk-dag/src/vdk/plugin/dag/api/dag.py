# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
import abc
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.dag.remote_data_job import JobStatus


@dataclass
class SingleJob:
    """
    This class represents a single job to be executed.

    :param job_name: the name of the job.
    :param team_name: the name of the team that owns the job.
    :param fail_dag_on_error: boolean flag indicating whether the job should be executed.
    :param arguments: JSON-serializable dictionary of arguments to be passed to the job.
    :param depends_on: list of names of jobs that this job depends on.
    """

    job_name: str
    team_name: str = None
    fail_dag_on_error: bool = True
    arguments: dict = None
    depends_on: List[str] = field(default_factory=list)


@dataclass
class DAG(SingleJob):
    """
    This class represents a DAG Job, which is a single job itself and consists of single jobs - the orchestrated ones.

    :param jobs: list of the orchestrated jobs
    """

    jobs: List[SingleJob] = field(default_factory=list)


class IDagInput(abc.ABC):
    """
    This class is responsible for the DAG job run.
    """

    @abstractmethod
    def run_dag(self, dag: DAG):
        """
        Runs the given DAG job.

        :param dag: the DAG job to be run
        :return:
        """
        pass


class IDagJobStatus(abc.ABC):
    """
    This class is responsible for the DAG job status checks.
    """

    @abstractmethod
    def get_job_status(self, job_name: str) -> Optional[JobStatus]:
        """
        Get job status.
        :return: JobStatus
        """
        pass

    @abstractmethod
    def get_all_jobs_execution_status(self) -> Optional[Dict[str, JobStatus]]:
        """
        Fetches the statuses of all jobs in the latest DAG execution.

        :return: Dict[str, JobStatus] - A dictionary where keys are job names and values are their statuses.
        """
        pass

    @abstractmethod
    def get_jobs_execution_status(
        self, job_names: List[str]
    ) -> Optional[Dict[str, JobStatus]]:
        """
        Fetches the execution statuses of specified jobs.

        :param job_names: List[str] - A list of job names whose statuses are to be fetched.
        :return: Dict[str, JobStatus] - A dictionary where keys are job names from the input list and values are their
         statuses.
        """
        pass
