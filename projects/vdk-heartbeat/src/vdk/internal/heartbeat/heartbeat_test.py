# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from abc import ABC
from abc import abstractmethod

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class HeartbeatTest(ABC):
    """
    Interface for defing tests
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


def create_test_instance(config: Config) -> HeartbeatTest:
    import importlib

    module = importlib.import_module(config.database_test_module_name)
    class_ = getattr(module, config.database_test_class_name)
    log.info(
        f"Run test instance: {config.database_test_module_name}.{config.database_test_class_name}"
    )
    instance = class_(config)
    return instance
