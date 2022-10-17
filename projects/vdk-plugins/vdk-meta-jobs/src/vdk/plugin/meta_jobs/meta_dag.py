# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import pprint
import sys
from graphlib import TopologicalSorter
from typing import Any
from typing import Dict
from typing import List

from vdk.plugin.meta_jobs.cached_data_job_executor import TrackingDataJobExecutor
from vdk.plugin.meta_jobs.meta import TrackableJob
from vdk.plugin.meta_jobs.remote_data_job_executor import RemoteDataJobExecutor

log = logging.getLogger(__name__)


class MetaJobsDag:
    def __init__(self, team_name: str):
        self._team_name = team_name
        self._topological_sorter = TopologicalSorter()
        self._finished_jobs = []
        self._job_executor = TrackingDataJobExecutor(RemoteDataJobExecutor())

    def build_dag(self, jobs: List[Dict]):
        for job in jobs:
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
                log.info(f"Data Job {node} has started.")

            for node in self._get_finalized_jobs():
                if node not in self._finished_jobs:
                    log.info(f"Data Job {node} has finished.")
                    self._topological_sorter.done(node)
                    self._job_executor.finalize_job(node)
                    self._finished_jobs.append(node)

    def __repr__(self):
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
        self._job_executor.start_job(node)

    def _get_finalized_jobs(self) -> List:
        return self._job_executor.get_finished_job_names()
