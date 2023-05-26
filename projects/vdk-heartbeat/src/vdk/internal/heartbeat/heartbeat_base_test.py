# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from abc import ABC
from abc import abstractmethod

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class HeartbeatBaseTest(ABC):
    """
    Template for defing tests
    """

    def __init__(self, config: Config):
        self.config = config

    @LogDecorator(log)
    @abstractmethod
    def setup(self):
        """
        Setup the test and all that is necessary
        """
        pass

    def __exit__(self, *exc):
        self.clean_up()

    @LogDecorator(log)
    @abstractmethod
    def clean_up(self):
        """
        After the test is finished it cleans up all resources used by the test.
        """
        pass

    @LogDecorator(log)
    @abstractmethod
    def execute_test(self):
        """
        Execute the test and run assertion and verification. If method returns then test has passed.
        If method throws an exception then test has failed.
        """
        pass

    @LogDecorator(log)
    def run_test(self):
        try:
            self.setup()
            self.execute_test()
        except:
            log.info("Heartbeat has failed.")
            if self.config.clean_up_on_failure:
                log.info("Heartbeat clean up on failure.")
                self.clean_up()
            raise
