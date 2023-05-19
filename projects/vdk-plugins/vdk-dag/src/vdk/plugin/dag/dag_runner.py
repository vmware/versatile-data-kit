# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import Dict
from typing import List
from typing import Optional

from vdk.plugin.dag.api.dag import IDagInput
from vdk.plugin.dag.dag import Dag

TEAM_NAME: Optional[str] = None
DAG_CONFIG = None
JOB_NAME: Optional[str] = None
EXECUTION_ID: Optional[str] = None

log = logging.getLogger(__name__)


def get_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


class DagInput(IDagInput):
    """
    This module is responsible for the execution of DAG of Data Jobs.
    """

    def run_dag(self, jobs: List[Dict]):
        """
        Runs the DAG of jobs - initializes it, builds it, executes it and logs the summary.

        :param jobs: the list of jobs that are part of the DAG
        :return:
        """
        dag = Dag(TEAM_NAME, DAG_CONFIG, JOB_NAME, EXECUTION_ID)
        dag.build_dag(jobs)
        dag.execute_dag()
        log.info(f"DAG summary:\n{dag}")
