# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from airflow.models import BaseOperator


class VDKOperator(BaseOperator):
    def __init__(
        self,
        conn_id,
        job_name,
        team_name,
    ):
        """ """
        pass

    def execute(self, context: Any):
        """

        :param context:
        :return:
        """
        pass
