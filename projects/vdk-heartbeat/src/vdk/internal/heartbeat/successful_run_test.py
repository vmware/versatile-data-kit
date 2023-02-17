# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_test import HeartbeatTest
from vdk.internal.heartbeat.job_controller import JobController
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class SuccessfulRunTest(HeartbeatTest):
    """
    Very simple test that just waits for the job to execute once.
    It verifies the data job completed successfully.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.__job_controller = JobController(config)

    @LogDecorator(log)
    def setup(self):
        pass

    @LogDecorator(log)
    def clean_up(self):
        pass

    @LogDecorator(log)
    def execute_test(self):
        status = None
        success_status = "succeeded"
        try:
            status = self.__job_controller.check_job_execution_finished()
        except Exception as e:
            raise AssertionError(
                "Successful run test failed with timeout. "
                f"It was waiting for data job {self.config.job_name} to complete "
                f"successfully. However the job did not do it in time. "
                f"Check data job logs for possible errors."
            )
        if status != success_status:
            raise AssertionError(
                "Successful run test failed with unexpected data job status. "
                f"It was waiting for data job {self.config.job_name} to complete "
                f"with status '{success_status}'. However the job completed with status {status}. "
                f"Check the data job logs for errors."
            )
