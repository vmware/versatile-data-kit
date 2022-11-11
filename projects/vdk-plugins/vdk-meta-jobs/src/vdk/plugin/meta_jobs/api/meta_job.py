# Copyright 2021 VMware, Inc.
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
    fail_meta_job_on_error: bool = True
    depends_on: List[str] = field(default_factory=list)


@dataclass
class MetaJob(SingleJob):
    """
    TODO
    """

    jobs: List[SingleJob] = field(default_factory=list)


class IMetaJobInput(abc.ABC):
    @abstractmethod
    def run_meta_job(self, meta_job: MetaJob):
        """
        TODO
        :param meta_job:
        :return:
        """
        pass
