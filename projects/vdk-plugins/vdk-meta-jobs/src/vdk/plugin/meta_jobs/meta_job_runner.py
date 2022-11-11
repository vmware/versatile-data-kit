# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.meta_jobs.api.meta_job import IMetaJobInput
from vdk.plugin.meta_jobs.meta_dag import MetaJobsDag

TEAM_NAME: Optional[str] = None

log = logging.getLogger(__name__)


def get_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


class MetaJobInput(IMetaJobInput):
    def run_meta_job(self, jobs: List[Dict]):
        dag = MetaJobsDag(TEAM_NAME)
        dag.build_dag(jobs)
        dag.execute_dag()
        log.info(f"Meta job summary:\n{dag}")
