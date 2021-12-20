# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# TODO: this is basically a copy of VDK JobConfig in vdk-core
import configparser
import fileinput
import logging
import os
import sys

from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.utils.control_utils import read_config_ini_file


log = logging.getLogger(__name__)


class JobConfig:
    """
    User facing configuration of a Data Job.
    For detailed documentation on each property see template-job/config.ini
    """

    def __init__(self, data_job_path):
        self._config_ini = configparser.ConfigParser()
        self._config_file = os.path.join(data_job_path, "config.ini")
        if not os.path.isfile(self._config_file):
            raise VDKException(
                what="Cannot extract job Configuration",
                why=f"Configuration file config.ini is missing in data job path: {data_job_path}",
                consequence="Cannot deploy and configure the data job without config.ini file.",
                countermeasure="config.ini must be in the root of the data job folder. "
                "Make sure the file is created "
                "or double check the data job path is passed correctly.",
            )
        read_config_ini_file(
            config_parser=self._config_ini, configuration_file_path=self._config_file
        )

    def get_team(self):
        return self._get_value("owner", "team")

    def set_team_if_exists(self, value):
        """
        If 'team' option exists in section 'owner' of config.ini, value param is assigned to it and
        config.ini file is overwritten with the new team value.
        Returns True if team is found and successfully set to 'value' in config.ini, False - otherwise
        """
        return self._set_value("owner", "team", value)

    def get_schedule_cron(self):
        return self._get_value("job", "schedule_cron")

    def get_enable_execution_notifications(self):
        return self._get_boolean(
            "contacts", "enable_execution_notifications", fallback=True
        )

    def get_notification_delay_period_minutes(self):
        return self._get_positive_int(
            "contacts", "notification_delay_period_minutes", fallback=240
        )

    def get_contacts_notified_on_job_failure_user_error(self):
        return self._get_contacts("notified_on_job_failure_user_error")

    def get_contacts_notified_on_job_failure_platform_error(self):
        return self._get_contacts("notified_on_job_failure_platform_error")

    def get_contacts_notified_on_job_success(self):
        return self._get_contacts("notified_on_job_success")

    def get_contacts_notified_on_job_deploy(self):
        return self._get_contacts("notified_on_job_deploy")

    def _get_boolean(self, section, key, fallback=None):
        return self._config_ini.getboolean(section, key, fallback=fallback)

    def _get_positive_int(self, section, key, fallback=None):
        try:
            value = self._config_ini.getint(section, key, fallback=fallback)
            if value <= 0:
                raise ValueError()
            return value
        except ValueError:
            raise VDKException(
                what=f"The configuration '{key}' property in the job's config.ini file is not valid.",
                why=f"The '{key}' configuration should be a positive integer, "
                f"but instead '{self._get_value(section, key)}' is found.",
                consequence="Cannot configure the data job without valid configuration.",
                countermeasure=f"Change the value of the '{key}' property in the job's config.ini file to "
                f"a positive integer and redeploy the job.",
            )

    def _get_value(self, section, key):
        if self._config_ini.has_option(section, key):
            return self._config_ini.get(section, key)
        return ""

    def _set_value(self, section, key, value):
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
        if contacts_str:
            return [x.strip() for x in contacts_str.split(";")]
        return []
