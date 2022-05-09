# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Any
from typing import Dict
from typing import Optional

from airflow.models import BaseOperator

log = logging.getLogger(__name__)


class VDKOperator(BaseOperator):
    """
    Operator used to start a Data Job execution.
    Can be used synchronously or asynchronously.

    :param conn_id: Required. The ID of the Airflow connection used to connect to the Control Service
    :param job_name: Required. Name of the job which will have an execution triggered
    :param team_name: Required. Name of the team the job belongs to
    :param asynchronous: Whether the operator runs asynchronously or not. If False, the operator will wait for the job to complete before returning
    :param wait_seconds: How long to wait in between checking whether the execution is complete. Used only if asynchronous is set to False
    :param timeout_seconds: How long until checking whether the execution is complete times out. Used only if asynchronous is set to False
    """

    def __init__(
        self,
        conn_id: str,
        job_name: str,
        team_name: str,
        asynchronous: bool = False,
        wait_seconds: float = 3,
        timeout_seconds: Optional[float] = 60 * 60,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.job_name = job_name
        self.team_name = team_name
        self.asynchronous = asynchronous
        self.wait_seconds = wait_seconds
        self.timeout_seconds = timeout_seconds

    def execute(self, context: Dict[Any, Any]) -> str:
        """
        Starts the job execution. If asynchronous is set to False, this method will wait
        for the job to complete before returning.

        :param context: Airflow context passed through the DAG
        :return: The job execution ID
        """
        pass
