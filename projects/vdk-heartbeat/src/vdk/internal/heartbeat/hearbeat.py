# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

from vdk.internal.heartbeat.config import Config
from vdk.internal.heartbeat.heartbeat_test import create_test_instance
from vdk.internal.heartbeat.heartbeat_test import HeartbeatTest
from vdk.internal.heartbeat.job_controller import JobController
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
        self._config = config

    @TestDecorator()
    def run(self):
        run_test = create_test_instance(self._config)
        job_controller = JobController(self._config)

        try:
            job_controller.login()
            job_controller.create_job()
            job_controller.deploy_job()

            job_controller.check_list_jobs()
            job_controller.check_deployments()
            job_controller.disable_deployment()
            job_controller.check_deployments(enabled=False)

            run_test.setup()

            job_controller.enable_deployment_and_update_vdk_version()
            job_controller.show_job_details()

            run_test.execute_test()
            job_controller.show_last_job_execution_logs()

            job_controller.disable_deployment()

            if self._config.check_manual_job_execution:
                job_controller.check_job_execution_finished()
                job_controller.start_job_execution()
                job_controller.check_job_execution_finished()

            self.clean(run_test, job_controller)
            log.info("Heartbeat has finished successfully.")
        except:
            log.info("Heartbeat has failed.")
            job_controller.show_job_details()
            job_controller.show_last_job_execution_logs()
            if self._config.clean_up_on_failure:
                log.info("Heartbeat clean up on failure.")
                self.clean(run_test, job_controller)
            raise

    @staticmethod
    def clean(run_test: HeartbeatTest, job_controller: JobController):
        job_controller.login()
        job_controller.delete_job()
        run_test.clean_up()
