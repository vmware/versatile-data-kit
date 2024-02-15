# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import fileinput
import logging
import os
import pathlib
import re
import sys
from configparser import ConfigParser
from configparser import MissingSectionHeaderError
from enum import Enum
from typing import Dict
from typing import List
from typing import Union

from vdk.internal.core.config import convert_value_to_type_of_default_type
from vdk.internal.core.errors import VdkConfigurationError


log = logging.getLogger(__name__)


class JobConfigKeys(str, Enum):
    TEAM = "team"
    SCHEDULE_CRON = "schedule_cron"
    PYTHON_VERSION = "python_version"
    ENABLE_EXECUTION_NOTIFICATIONS = "enable_execution_notifications"
    NOTIFICATION_DELAY_PERIOD_MINUTES = "notification_delay_period_minutes"
    NOTIFIED_ON_JOB_FAILURE_USER_ERROR = "notified_on_job_failure_user_error"
    NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR = "notified_on_job_failure_platform_error"
    NOTIFIED_ON_JOB_SUCCESS = "notified_on_job_success"
    NOTIFIED_ON_JOB_DEPLOY = "notified_on_job_deploy"
    ENABLE_ATTEMPT_NOTIFICATIONS = "enable_attempt_notifications"
    DB_DEFAULT_TYPE = "db_default_type"


class JobConfig:
    """
    User facing configuration of a Data Job.
    For more see the user wiki
    """

    def __init__(
        self, data_job_path: Union[pathlib.Path, str], should_fail_missing_config=False
    ):
        self._config_ini = configparser.ConfigParser()
        self._config_file = os.path.join(data_job_path, "config.ini")
        self._should_fail_missing_config = should_fail_missing_config

        if not os.path.isfile(self._config_file):
            if should_fail_missing_config:
                raise VdkConfigurationError(
                    "Error while loading config.ini file",
                    "Cannot extract job Configuration",
                    f"Configuration file config.ini is missing in data job path: {data_job_path}",
                    "Cannot deploy and configure the data job without config.ini file.",
                    "config.ini must be in the root of the data job folder. "
                    "Make sure the file is created "
                    "or double check the data job path is passed correctly.",
                )
            else:
                log.info("Missing config.ini file.")

        self._read_config_ini_file(
            config_parser=self._config_ini, configuration_file_path=self._config_file
        )

    def get_team(self) -> str:
        """
        Specified which is the team that owns the data job.

        Teams is a way to group data jobs that belong together and are managed by same people.
        It will control who has permissions to manages the data job.
        """
        return self._get_value("owner", JobConfigKeys.TEAM.value)

    def set_team_if_exists(self, value):
        """
        If 'team' option exists in section 'owner' of config.ini, value param is assigned to it and
        config.ini file is overwritten with the new team value.
        Returns True if team is found and successfully set to 'value' in config.ini, False - otherwise
        """
        return self._set_value("owner", JobConfigKeys.TEAM.value, value)

    def get_schedule_cron(self) -> str:
        return self._get_value("job", JobConfigKeys.SCHEDULE_CRON.value)

    def get_python_version(self) -> str:
        return str(self._get_value("job", JobConfigKeys.PYTHON_VERSION.value))

    def get_enable_execution_notifications(self) -> bool:
        return self._get_boolean(
            "contacts",
            JobConfigKeys.ENABLE_EXECUTION_NOTIFICATIONS.value,
            fallback=True,
        )

    def get_notification_delay_period_minutes(self) -> int:
        return self._get_positive_int(
            "contacts",
            JobConfigKeys.NOTIFICATION_DELAY_PERIOD_MINUTES.value,
            fallback=240,
        )

    def get_contacts_notified_on_job_failure_user_error(self) -> List[str]:
        """
        List of email addresses to be notified on job execution failure caused by user code or user configuration problem
        """
        return self._get_contacts(
            JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR.value
        )

    def get_contacts_notified_on_job_failure_platform_error(self) -> List[str]:
        """
        List of email addresses to be notified on job execution failure caused by a platform problem.
        """
        return self._get_contacts(
            JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR.value
        )

    def get_contacts_notified_on_job_success(self) -> List[str]:
        """
        List of email addresses to be notified on job execution success.
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS.value)

    def get_contacts_notified_on_job_deploy(self) -> List[str]:
        """
        List of email addresses to be notified of job deployment outcome.
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_DEPLOY.value)

    def get_enable_attempt_notifications(self) -> bool:
        """
        Flag to enable or disable the email notifications on a single attempt
        (in other words each automatic retry will send an email).
        """
        enable_attempt_notif_value = self._get_value(
            "contacts", JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value
        )
        if (
            enable_attempt_notif_value == ""
        ):  # if the parameter hasn't been set in config.ini, we default to False
            return False
        else:
            return convert_value_to_type_of_default_type(
                JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value,
                enable_attempt_notif_value,
                False,
            )

    def get_db_type(self) -> str:
        """
        The default database type used by the job (IMPALA, PRESTO)
        """
        return self._get_value("job", JobConfigKeys.DB_DEFAULT_TYPE.value)

    def get_vdk_options(self) -> Dict[str, str]:
        if self._config_ini.has_section("vdk"):
            return dict(self._config_ini["vdk"])
        else:
            return {}

    def _get_value(self, section, key):
        if self._config_ini.has_option(section, key):
            return self._config_ini.get(section, key)
        return ""

    def _set_value(self, section, key, value) -> bool:
        success = False
        if self._config_ini.has_option(section, key):
            for line in fileinput.input(self._config_file, inplace=1):
                if line.replace(" ", "").startswith(f"{key}="):
                    success = True
                    line = f"{key} = {value}\n"
                sys.stdout.write(line)
        return success

    def _get_contacts(self, key):
        contacts_str = self._get_value("contacts", key).strip()
        contacts = []
        if contacts_str:
            contacts = [x.strip() for x in re.split("[;,]", contacts_str)]
        return contacts

    def _get_boolean(self, section, key, fallback=None) -> bool:
        return self._config_ini.getboolean(section, key, fallback=fallback)

    def _get_positive_int(self, section, key, fallback=None) -> int:
        try:
            value = self._config_ini.getint(section, key, fallback=fallback)
            if value <= 0:
                raise ValueError()
            return value
        except ValueError:
            raise VdkConfigurationError(
                "Invalid configuration property.",
                f"The configuration '{key}' property in the job's config.ini file is not valid.",
                f"The '{key}' configuration should be a positive integer, "
                f"but instead '{self._get_value(section, key)}' is found.",
                "Cannot configure the data job without valid configuration.",
                f"Change the value of the '{key}' property in the job's config.ini file to "
                f"a positive integer and redeploy the job.",
            )

    @staticmethod
    def _read_config_ini_file(
        config_parser: ConfigParser, configuration_file_path: str
    ) -> None:
        """
        Read the Data Job config.ini file.

        :param config_parser: ConfigParser instance to be used for reading the
        configuration file.
        :param configuration_file_path: Path of the config.ini file
        """
        try:
            config_parser.read(configuration_file_path)
        except (MissingSectionHeaderError, Exception) as e:
            log.debug(e, exc_info=True)  # Log the traceback in DEBUG mode.
            raise VdkConfigurationError(
                "Error while parsing config file.",
                "Cannot parse the Data Job configuration file"
                f" {configuration_file_path}.",
                f"Configuration file config.ini is probably corrupted. Error: {e}",
                "Cannot deploy and configure the data job "
                "without "
                " properly set config.ini file.",
                countermeasures="config.ini must be UTF-8 compliant. "
                "Make sure the file does not contain special "
                "Unicode characters, or that your text editor "
                "has not added such characters somewhere in the file.",
            )
