# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import getpass
import logging
import re
from os import environ
from time import time
from typing import Optional

log = logging.getLogger(__name__)


class Config:
    DEFAULT_OP_ID = f"{getpass.getuser()}_{int(time())}"

    def __init__(self, config_file=None):
        self._config_ini = configparser.ConfigParser()
        if config_file:
            log.info(f"Loading configuration file: {config_file}")
            self._config_ini.read(config_file)
            log.info(f"Configuration loaded: {self._config_ini.items()}")

        # VDK CLI Arguments for vdkcli login
        self.vdkcli_api_refresh_token = self._get_atleast_one_value(
            "VDKCLI_OAUTH2_REFRESH_TOKEN", "VDK_HEARTBEAT_API_TOKEN", is_required=False
        )
        # If no value is found, argument will not be passed and default will be used
        self.vdkcli_oauth2_uri = self._get_atleast_one_value(
            "VDKCLI_OAUTH2_URI", "VDK_HEARTBEAT_API_TOKEN_AUTH_URL", is_required=False
        )

        self.op_id = self.get_value("VDK_HEARTBEAT_OP_ID", Config.DEFAULT_OP_ID)
        table_suffix = re.sub("[^a-z0-9_]", "_", self.op_id.lower())
        job_suffix = re.sub("[^a-z0-9-]", "-", self.op_id.lower())

        # Database configuration used by DatabaseTest.
        # Write access (to create drop tables and insert into tables) are DATABASE_TEST_DB is required
        self.DATABASE_HOST = self.get_value("DATABASE_HOST", is_required=False)
        self.DATABASE_PORT = int(self.get_value("DATABASE_PORT", 8080))
        self.DATABASE_USER = self.get_value("DATABASE_USER", is_required=False)
        self.DATABASE_PASS = self.get_value("DATABASE_PASS", is_required=False)
        self.DATABASE_USE_SSL = self.get_value("DATABASE_USE_SSL", "yes").lower() in (
            "yes",
            "y",
            "true",
            1,
        )
        self.DATABASE_VERIFY_SSL = self.get_value(
            "DATABASE_VERIFY_SSL", "yes"
        ).lower() in ("yes", "y", "true", 1)
        self.DATABASE_AUTHN_TYPE = self.get_value(
            "DATABASE_AUTHENTICATION_MECHANISM", is_required=False
        )

        # Database test configuration.
        self.DATABASE_TEST_DB = self.get_value(
            "DATABASE_TEST_DB", "taurus_testing_sandbox"
        )
        self.DATABASE_TEST_TABLE_SOURCE = self.get_value(
            "DATABASE_TEST_TABLE_SOURCE", f"vdk_heartbeat_source_{table_suffix}"
        )
        self.DATABASE_TEST_TABLE_DESTINATION = self.get_value(
            "DATABASE_TEST_TABLE_DESTINATION",
            f"vdk_heartbeat_destination_{table_suffix}",
        )
        self.DATABASE_TEST_TABLE_LOAD_DESTINATION = self.get_value(
            "DATABASE_TEST_TABLE_LOAD_DESTINATION",
            f"vdk_heartbeat_load_destination_{table_suffix}",
        )

        self.DATABASE_CONNECTION_TIMEOUT_SECONDS = int(
            self.get_value("DATABASE_CONNECTION_TIMEOUT_SECONDS", "180")
        )
        self.RUN_TEST_TIMEOUT_SECONDS = int(
            self.get_value("RUN_TEST_TIMEOUT_SECONDS", "1200")
        )

        # Ingestion test configuration
        # Target identifies where the data should be ingested into.
        self.INGEST_TARGET = self.get_value(
            "VDK_HEARTBEAT_INGEST_TARGET",
            "vdk-heartbeat-datasource",
        )

        """
        Indicates the ingestion method to be used. Example:
                    method="file" -> ingest to file
                    method="http" -> ingest using HTTP POST requests
                    method="kafka" -> ingest to kafka endpoint
        """
        self.INGEST_METHOD = self.get_value("VDK_HEARTBEAT_INGEST_METHOD", "http")

        # The name of the table, where the data should be ingested into.
        self.INGEST_DESTINATION_TABLE = self.get_value(
            "VDK_HEARTBEAT_INGEST_DESTINATION_TABLE",
            "vdk_heartbeat_ingestion_test",
        )

        # The time for which the data should be ingested.
        self.INGEST_TIMEOUT = self.get_value(
            "VDK_HEARTBEAT_INGEST_TIMEOUT",
            "300",
        )

        # The Control Service API URL (http://url/data-jobs) without data-jobs suffix
        # If no value is found, argument will not be passed and default will be used
        self.control_api_url = self._get_atleast_one_value(
            "CONTROL_API_URL", "VDK_HEARTBEAT_CONTROL_SERVICE_URL", is_required=False
        )

        # Deploy the job with a specific vdk version (optional). By default latest vdk is used.
        self.deploy_job_vdk_version = self.get_value(
            "VDK_HEARTBEAT_DEPLOY_JOB_VDK_VERSION", is_required=False
        )

        # Job name deployed during the test
        self.job_name = self.get_value(
            "JOB_NAME", f"vdk-heartbeat-data-job-{job_suffix}"[0:45]
        )
        """
        The team of the data job ot use.
        """
        self.job_team = self.get_value("JOB_TEAM", "taurus")
        """
            If set to true it will set job notifications to be sent on deploy and execution of the test jobs.
        """
        self.job_notification_mail = self.get_value(
            "JOB_NOTIFICATION_MAIL", None, is_required=False
        )
        """
        The location where data jobs directories can be found.
        Leave empty (default) to user embedded data jobs in vdk-heartbeat.
        """
        self.data_job_directory_parent = self.get_value(
            "DATAJOB_DIRECTORY_PARENT", None, is_required=False
        )
        """
        Control the location of hte data job name with parent directory specified by DATAJOB_DIRECTORY_PARENT
        If DATAJOB_DIRECTORY_PARENT is left by default vdk-heartbeat provides following options:
        impala, trino, simple, empty
        JOB_RUN_TEST_* should be set accordingly.
        """
        self.data_job_directory_name = self.get_value(
            "DATAJOB_DIRECTORY_NAME", "impala"
        )
        """
        Control the module name of the "run_test" executed when job is scheduled in cloud.
        Generally should be used alongside JOB_RUN_TEST_CLASS_NAME, DATAJOB_DIRECTORY_NAME

        the module name (it can be provided by external application)
        In vdk-heartbeat following are supported:
        taurus.vdk.heartbeat.empty_run_test
        taurus.vdk.heartbeat.simple_run_test
        taurus.vdk.heartbeat.trino_database_test
        taurus.vdk.heartbeat.impala_database_test (default)
        """
        self.database_test_module_name = self.get_value(
            "JOB_RUN_TEST_MODULE_NAME", "vdk.internal.heartbeat.impala_database_test"
        )
        """
        Control the class name of the "run_test" executed when job is schedudled in cloud.
        Generally should be used alongside JOB_RUN_TEST_MODULE_NAME, DATAJOB_DIRECTORY_NAME

        the module name (it can be provided by external application)
        In vdk-heartbeat following are supported:
        EmptyRunTest
        SimpleRunTest
        TrinoDatabaseRunTest
        ImpalaDatabaseHeartbeatTest (default)
        """
        self.database_test_class_name = self.get_value(
            "JOB_RUN_TEST_CLASS_NAME", "ImpalaDatabaseHeartbeatTest"
        )
        self.db_default_type = self.get_value("DB_DEFAULT_TYPE", "IMPALA")
        self.vdk_command_name = self.get_value("VDK_COMMAND_NAME", "vdkcli")

        self.clean_up_on_failure = self._string_to_bool(
            self.get_value("CLEAN_UP_ON_FAILURE", "true", False)
        )
        """
        Flag is used to check if manual execution needs to be run as part of the heartbeat test.
        In manual execution - it will disable the scheduled execution and start manually execution
        and wait it to finish successfully. It will not verify the logic (e.g it will not run run_test for a second time).
        It defaults to True.
        """
        self.check_manual_job_execution = self._string_to_bool(
            self.get_value("CHECK_MANUAL_JOB_EXECUTION", "true", False)
        )

        """
        Flag is used to check if Trino template execution needs to be run as part of the heartbeat test.
        If set to true, the vdk_heartbeat_data_job/trino job will perform a step which will execute a template.
        It defaults to True.
        """
        self.check_template_execution = self._string_to_bool(
            self.get_value("CHECK_TEMPLATE_EXECUTION", "true", False)
        )

        """
        Set file path to the JUNIT XML Test report file. If left empty , the file will not be generated.
        The file does not need to exists but all parent directories must exist.
        """
        self.report_junit_xml_file_path = self.get_value(
            "REPORT_JUNIT_XML_FILE_PATH", "tests.xml"
        )

    def get_value(self, key: str, default_value: str = None, is_required=True):
        value = environ.get(key, None)
        if not value:
            value = self._config_ini["DEFAULT"].get(key, default_value)
        if not value and is_required:
            raise ValueError(
                "Error occurred:\n"
                f"What: Cannot configure heartbeat test\n"
                f"Why: Missing required configuration with key {key}\n"
                f"Consequences: The heartbeat will abort\n"
                f"Countermeasures: Set as required configuration either as environment variable or in the config file."
            )
        return value

    def _get_atleast_one_value(self, key1: str, key2: str, is_required=True):
        value1 = self.get_value(key1, is_required=False)
        value2 = self.get_value(key2, is_required=False)

        if is_required and (value1 is None) and (value2 is None):
            raise ValueError(
                "Error occurred:\n"
                f"What: Cannot configure heartbeat test\n"
                f"Why: Missing required configuration with either key {key1} or key {key2}\n"
                f"Consequences: The heartbeat will abort\n"
                f"Countermeasures: Set as required configuration either as environment variable or in the config file."
            )

        return value1 if value1 is not None else value2

    @staticmethod
    def _string_to_bool(v):
        return v and v.lower() in ("yes", "true", "t", "1")
