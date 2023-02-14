# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import os

import pytest
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.job.job_config import JobConfig
from vdk.internal.control.utils import cli_utils
from vdk.internal.test_utils import find_test_resource


class TestSetTeam:
    @pytest.fixture(autouse=True)
    def setup_method(self, tmpdir):
        self.tmp_copy_job_test_path = os.path.join(tmpdir, "my-tmp-test-job")
        self.test_job_path = find_test_resource("test-job")
        self.tmp_copy_job_test_config_ini_path = os.path.join(
            self.tmp_copy_job_test_path, "config.ini"
        )

        cli_utils.copy_directory(self.test_job_path, self.tmp_copy_job_test_path)

    def test_set_team(self):
        self._perform_set_team_test(
            "my_unique_team_name", JobConfig(self.tmp_copy_job_test_path)
        )

    def test_set_empty_team(self):
        self._perform_set_team_test("", JobConfig(self.tmp_copy_job_test_path))

    def test_set_team_with_spaces(self):
        self._perform_set_team_test(
            "my unique team name", JobConfig(self.tmp_copy_job_test_path)
        )

    def test_set_team_with_no_team_in_config_ini(self):
        # remove all contents of config.ini (including team option)
        config_ini_file = open(self.tmp_copy_job_test_config_ini_path, "w")
        config_ini_file.truncate(0)
        config_ini_file.close()

        job_config = JobConfig(self.tmp_copy_job_test_path)

        assert (
            not job_config.get_team()
        ), f"empty config.ini file should not provide a team"

        assert not job_config.set_team_if_exists(
            "my unique team name"
        ), f"set_team_if_exists was supposed to return False if there is no team option in config.ini"

    def _perform_set_team_test(self, team_name, job_config):
        assert job_config.set_team_if_exists(
            team_name
        ), f"team option was expected to be present in: {self.tmp_copy_job_test_config_ini_path}"

        with open(self.tmp_copy_job_test_config_ini_path) as f:
            assert (
                team_name in f.read()
            ), f"set_team_if_exists failed to write team {team_name} in: {self.tmp_copy_job_test_config_ini_path}"

    def test_notification_delay_period_minutes(self):
        self.__create_config_ini(
            self.tmp_copy_job_test_config_ini_path,
            [("notification_delay_period_minutes", "100")],
        )
        job_config = JobConfig(self.tmp_copy_job_test_path)
        assert job_config.get_notification_delay_period_minutes() == 100

    def test_invalid_notification_delay_period_minutes(self):
        self.__create_config_ini(
            self.tmp_copy_job_test_config_ini_path,
            [("notification_delay_period_minutes", "invalid_value")],
        )
        job_config = JobConfig(self.tmp_copy_job_test_path)
        with pytest.raises(VDKException):
            job_config.get_notification_delay_period_minutes()

    def test_negative_notification_delay_period_minutes(self):
        self.__create_config_ini(
            self.tmp_copy_job_test_config_ini_path,
            [("notification_delay_period_minutes", "-100")],
        )
        job_config = JobConfig(self.tmp_copy_job_test_path)
        with pytest.raises(VDKException):
            job_config.get_notification_delay_period_minutes()

    def test_parse_notification_contacts(self):
        self.__create_config_ini(
            self.tmp_copy_job_test_config_ini_path,
            [
                ("notified_on_job_deploy", "a@abv.bg; b@dir.bg,   c@abv.bg ; d@dir.bg"),
                (
                    "notified_on_job_success",
                    "a@abv.bg; b@dir.bg,   c@abv.bg ; d@dir.bg",
                ),
                (
                    "notified_on_job_failure_user_error",
                    "a@abv.bg; b@dir.bg,   c@abv.bg ; d@dir.bg",
                ),
                (
                    "notified_on_job_failure_platform_error",
                    "a@abv.bg; b@dir.bg,   c@abv.bg ; d@dir.bg",
                ),
            ],
        )
        job_config = JobConfig(self.tmp_copy_job_test_path)
        assert job_config.get_contacts_notified_on_job_deploy() == [
            "a@abv.bg",
            "b@dir.bg",
            "c@abv.bg",
            "d@dir.bg",
        ]
        assert job_config.get_contacts_notified_on_job_success() == [
            "a@abv.bg",
            "b@dir.bg",
            "c@abv.bg",
            "d@dir.bg",
        ]
        assert job_config.get_contacts_notified_on_job_failure_user_error() == [
            "a@abv.bg",
            "b@dir.bg",
            "c@abv.bg",
            "d@dir.bg",
        ]
        assert job_config.get_contacts_notified_on_job_failure_platform_error() == [
            "a@abv.bg",
            "b@dir.bg",
            "c@abv.bg",
            "d@dir.bg",
        ]

    @staticmethod
    def __create_config_ini(file, contacts):
        config = configparser.ConfigParser()
        config.add_section("contacts")
        for k, v in contacts:
            config.set("contacts", k, v)
        with open(file, "w") as f:
            config.write(f)
