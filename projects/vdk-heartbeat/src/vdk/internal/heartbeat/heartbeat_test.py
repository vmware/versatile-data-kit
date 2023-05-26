# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from abc import ABC
from abc import abstractmethod

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_base_test import HeartbeatBaseTest
from vdk.internal.heartbeat.job_controller import JobController
from vdk.internal.heartbeat.tracing import LogDecorator

log = logging.getLogger(__name__)


class HeartbeatTest(HeartbeatBaseTest):
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
        self.__job_controller = JobController(config)

    @LogDecorator(log)
    def run_test(self):
        try:
            self.__job_controller.login()
            self.__job_controller.create_job()
            self.__job_controller.deploy_job()

            self.__job_controller.check_list_jobs()
            self.__job_controller.check_deployments()
            self.__job_controller.disable_deployment()
            self.__job_controller.check_deployments(enabled=False)

            self.setup()

            self.__job_controller.enable_deployment()
            self.__job_controller.show_job_details()

            self.execute_test()
            self.__job_controller.show_last_job_execution_logs()

            self.__job_controller.disable_deployment()

            if self.config.check_manual_job_execution:
                self.__job_controller.check_job_execution_finished()
                self.__job_controller.start_job_execution()
                self.__job_controller.check_job_execution_finished()

            self.clean()
            log.info("Heartbeat has finished successfully.")
        except:
            log.info("Heartbeat has failed.")
            self.__job_controller.show_job_details()
            self.__job_controller.show_last_job_execution_logs()
            if self.config.clean_up_on_failure:
                log.info("Heartbeat clean up on failure.")
                self.clean()
            raise

    def clean(self):
        self.__job_controller.login()
        self.__job_controller.delete_job()
        self.clean_up()
