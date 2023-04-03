# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.dags.api.dag import IDAGInput
from vdk.plugin.dags.dag import DAG

TEAM_NAME: Optional[str] = None
DAG_CONFIG = None

log = logging.getLogger(__name__)


def get_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


class DAGInput(IDAGInput):
    def run_dag(self, jobs: List[Dict]):
        dag = DAG(TEAM_NAME, DAG_CONFIG)
        dag.build_dag(jobs)
        dag.execute_dag()
        log.info(f"DAG summary:\n{dag}")
