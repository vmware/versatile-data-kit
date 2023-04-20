# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import abc
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import List


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
    fail_meta_job_on_error: bool = True
    arguments: dict = None
    depends_on: List[str] = field(default_factory=list)


@dataclass
class MetaJob(SingleJob):
    """
    This class represents a DAG Job, which is a single job itself and consists of single jobs - the orchestrated ones.

    :param jobs: list of the orchestrated jobs
    """

    jobs: List[SingleJob] = field(default_factory=list)


class IMetaJobInput(abc.ABC):
    """
    This class is responsible for the DAG job run.
    """

    @abstractmethod
    def run_meta_job(self, meta_job: MetaJob):
        """
        Runs the given DAG job.

        :param dag: the DAG job to be run
        :return:
        """
        pass
