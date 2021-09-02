# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import getpass
import logging
import re
from os import environ
from time import time

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
        self.vdkcli_api_refresh_token = self.get_value("VDKCLI_OAUTH2_REFRESH_TOKEN")
        self.vdkcli_oauth2_uri = self.get_value("VDKCLI_OAUTH2_URI")
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

        # The Taurus Control Service API URL (http://url/data-jobs) without data-jobs suffix
        self.control_api_url = self.get_value("CONTROL_API_URL")

        # Job name deployed during the test
        self.job_name = self.get_value(
            "JOB_NAME", f"vdk-heartbeat-data-job-{job_suffix}"
        )
        self.job_version = self.get_value("JOB_VERSION", "HEAD")
        self.job_team = self.get_value("JOB_TEAM", "taurus")
        self.job_notification_mail = self.get_value(
            "JOB_NOTIFICATION_MAIL", None, is_required=False
        )
        self.data_job_directory_parent = self.get_value(
            "DATAJOB_DIRECTORY_PARENT", None, is_required=False
        )
        # by default possible options are: impala, trino, simple
        self.data_job_directory_name = self.get_value(
            "DATAJOB_DIRECTORY_NAME", "impala"
        )
        self.database_test_module_name = self.get_value(
            "JOB_RUN_TEST_MODULE_NAME", "taurus.vdk.heartbeat.impala_database_test"
        )
        self.database_test_class_name = self.get_value(
            "JOB_RUN_TEST_CLASS_NAME", "ImpalaDatabaseHeartbeatTest"
        )
        self.db_default_type = self.get_value("DB_DEFAULT_TYPE", "IMPALA")
        self.vdk_command_name = self.get_value("VDK_COMMAND_NAME", "vdkcli")

        self.clean_up_on_failure = self._string_to_bool(
            self.get_value("CLEAN_UP_ON_FAILURE", "true", False)
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

    @staticmethod
    def _string_to_bool(v):
        return v and v.lower() in ("yes", "true", "t", "1")
