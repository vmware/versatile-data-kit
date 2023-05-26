# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_base_test import HeartbeatBaseTest
from vdk.internal.heartbeat.reporter import TestDecorator

log = logging.getLogger(__name__)


class Heartbeat:
    """
    Executes a heartbeat test that verifies the correct behaviour of Data Pipelines.

    It has the following steps:
    - Creates a Data Job using VDK CLI for managing jobs
    - Deploys the data job using the same Versatile Data Kit SDK
    - Run database test to verify the job works correctly in cloud runtime.
    - Deletes the Data Job using VDK CLI
    """

    def __init__(self, config: Config):
        self.config = config

    @TestDecorator()
    def run(self):
        create_test_instance(self.config).run_test()


def create_test_instance(config: Config) -> HeartbeatBaseTest:
    import importlib

    try:
        module = importlib.import_module(config.database_test_module_name)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"Configured database_test_module_name is not found. Error was: {e}.\n"
            f"Make sure module {config.database_test_module_name} exists.\n"
            f"Check if the module name in the configuration is not misspelled "
            f"or if some 3rd party library needs to be installed to provide it."
        ) from None
    try:
        class_ = getattr(module, config.database_test_class_name)
    except AttributeError as e:
        raise AttributeError(
            f"Configured database_test_class_name is not found. Error was: {e}.\\n"
            f"Make sure class {config.database_test_class_name} exists.\n"
            f"Check if the class name in the configuration is not misspelled "
            f"or if some 3rd party library needs to be installed to provide it."
        ) from None
    log.info(
        f"Run test instance: {config.database_test_module_name}.{config.database_test_class_name}"
    )
    instance = class_(config)
    return instance
