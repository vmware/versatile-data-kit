# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import abc
from dataclasses import dataclass

from vdk.plugin.meta_jobs.api import meta_job


class IDataJobExecutor(abc.ABC):
    @abc.abstractmethod
    def start_job(self, job_name: str, team_name: str):
        """
        Start an execution of a data job and returns its execution id
        :param job_name:
        :param team_name:
        :return: execution id
        """
        pass

    @abc.abstractmethod
    def status_job(self, job_name: str, team_name: str, execution_id: str):
        """
        Get the current status of a data job execution
        :param job_name:
        :param team_name:
        :param execution_id:
        :return: status in string as defined by Control Service API
        """
        pass

    @abc.abstractmethod
    def details_job(self, job_name: str, team_name: str, execution_id: str) -> dict:
        """
        Get the current status of a data job execution
        :param job_name:
        :param team_name:
        :param execution_id:
        :return: status in string as defined by Control Service API
        """
        pass


@dataclass
class TrackableJob(meta_job.SingleJob):
    status: str = None
    execution_id: str = None
    details: dict = None
    start_attempt = 0
    last_status_time = 0
