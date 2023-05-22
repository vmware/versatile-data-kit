# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import requests
from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_base_test import HeartbeatBaseTest
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class PingFrontendTest(HeartbeatBaseTest):
    """
    A simple test that pings the frontend to check if it started when deployed using helm
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.success_statuses = [200, 202, 204]
        self.url = config.control_api_url

    @LogDecorator(log)
    def setup(self):
        pass

    @LogDecorator(log)
    def clean_up(self):
        pass

    @LogDecorator(log)
    def execute_test(self):
        status = None
        try:
            response = requests.get(self.url)
            status = response.status_code
        except Exception as e:
            raise AssertionError(f"Request to {self.url} failed to complete")

        if status not in self.success_statuses:
            raise AssertionError(
                f"Request to {self.url} failed with status {status}"
                "Could not detect that frontend is running"
            )
