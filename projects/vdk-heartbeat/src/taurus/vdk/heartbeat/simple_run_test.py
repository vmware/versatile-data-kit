# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket
import time
import uuid
from datetime import datetime
from datetime import timedelta

from retrying import retry
from taurus.vdk.heartbeat.config import Config
from taurus.vdk.heartbeat.heartbeat_test import HeartbeatTest
from taurus.vdk.heartbeat.job_controller import JobController
from taurus.vdk.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class SimpleRunTest(HeartbeatTest):
    """
    Very simple test that just waits for the job to execute once.
    It's meant not to rely on any external systems (e.g. running database)
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
        wait_time_seconds = 30
        start_time = time.time()
        caught_exception = None
        while time.time() - start_time < self.config.RUN_TEST_TIMEOUT_SECONDS:
            log.info(f"Search for job property to set 'now' property.")
            try:
                props = self.__job_controller.get_job_properties()
                if props and "now" in props:
                    log.info(
                        f"Data Job has recorded successfully property 'now' = {props['now']}"
                    )
                    return
                else:
                    log.info(
                        f"Data is not available yet. Waiting {wait_time_seconds} seconds before trying again."
                    )
                    time.sleep(wait_time_seconds)
            except Exception as e:
                caught_exception = e
                log.info(
                    f"Error while querying for results. Waiting {wait_time_seconds} seconds before trying again. "
                    f"Error was {e}"
                )
                time.sleep(wait_time_seconds)
        if caught_exception:
            raise AssertionError(
                "Simple test failed with exception. See cause for more."
            ) from caught_exception
        else:
            raise AssertionError(
                "Simple test failed with timeout. "
                f"It was waiting for data job {self.config.job_name} to update its job properties "
                f"with key 'now' and value - current time. But the job did not do it in time. "
                f"Check data job logs for possible errors."
            )
