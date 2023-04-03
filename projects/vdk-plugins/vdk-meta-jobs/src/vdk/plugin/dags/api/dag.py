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
    TODO
    """

    job_name: str
    team_name: str = None
    fail_dag_on_error: bool = True
    depends_on: List[str] = field(default_factory=list)


@dataclass
class DAG(SingleJob):
    """
    TODO
    """

    jobs: List[SingleJob] = field(default_factory=list)


class IDAGInput(abc.ABC):
    @abstractmethod
    def run_dag(self, dag: DAG):
        """
        TODO
        :param dag:
        :return:
        """
        pass
