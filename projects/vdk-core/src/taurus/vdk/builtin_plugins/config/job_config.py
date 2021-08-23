# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import pathlib
from enum import Enum
from typing import List

from taurus.vdk.core.config import convert_value_to_type_of_default_type


class JobConfigKeys(str, Enum):
    TEAM = "team"
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

    def __init__(self, data_job_path: pathlib.Path):
        self._config_ini = configparser.ConfigParser()
        self._config_ini.read(str(data_job_path.joinpath("config.ini")))

    def get_team(self) -> str:
        """
        Specified which is the team that owns the data job.

        Teams is a way to group data jobs that belong together and are managed by same people.
        It will control who has permissions to manages the data job.
        """
        return self._get_value("owner", JobConfigKeys.TEAM)

    def get_contacts_notified_on_job_failure_user_error(self) -> List[str]:
        """
        List of email addresses to be notified on job execution failure caused by user code or user configuration problem
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR)

    def get_contacts_notified_on_job_failure_platform_error(self) -> List[str]:
        """
        List of email addresses to be notified on job execution failure caused by a platform problem.
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR)

    def get_contacts_notified_on_job_success(self) -> List[str]:
        """
        List of email addresses to be notified on job execution success.
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS)

    def get_contacts_notified_on_job_deploy(self) -> List[str]:
        """
        List of email addresses to be notified of job deployment outcome.
        """
        return self._get_contacts(JobConfigKeys.NOTIFIED_ON_JOB_DEPLOY)

    def get_enable_attempt_notifications(self) -> bool:
        """
        Flag to enable or disable the email notifications on a single attempt
        (in other words each automatic retry will sent an email).
        """
        enable_attempt_notif_value = self._get_value(
            "contacts", JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS
        )
        if (
            enable_attempt_notif_value == ""
        ):  # if the parameter hasn't been set in config.ini, we default to False
            return False
        else:
            return convert_value_to_type_of_default_type(
                JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS,
                enable_attempt_notif_value,
                False,
            )

    def get_db_type(self) -> str:
        """
        The default database type used by the job (IMPALA, PRESTO)
        """
        return self._get_value("job", JobConfigKeys.DB_DEFAULT_TYPE)

    def _get_value(self, section, key):
        if self._config_ini.has_option(section, key):
            return self._config_ini.get(section, key)
        return ""

    def _get_contacts(self, key):
        contacts_str = self._get_value("contacts", key).strip()
        if contacts_str:
            return [x.strip() for x in contacts_str.split(";")]
        return []
