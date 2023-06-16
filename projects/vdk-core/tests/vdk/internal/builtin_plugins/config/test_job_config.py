# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import configparser
import os
import pathlib
import shutil
import tempfile

import pytest
from vdk.internal.builtin_plugins.config.job_config import JobConfig
from vdk.internal.core.errors import VdkConfigurationError


class TestJobConfig:
    def setup_method(self, method):
        # Create a temporary directory
        self._test_dir = pathlib.Path(tempfile.mkdtemp())
        self._test_config_path = os.path.join(self._test_dir, "config.ini")
        cfg_string = """
   [owner]
     team = foo
   [contacts]
   notified_on_job_failure_user_error=a@test.com
   notified_on_job_failure_platform_error=b@test.com; asdf
   notified_on_job_success=c1@test.com;  c2@test.com
   notified_on_job_deploy=

   enable_attempt_notifications=yes

   [job]
   db_default_type=IMPALA
   """
        self._write_to_config_ini(self._test_dir, cfg_string)
        self._cfg = JobConfig(self._test_dir)

    def teardown_method(self, method):
        # Remove the directory after the test
        shutil.rmtree(self._test_dir)

    @staticmethod
    def _write_to_config_ini(directory: pathlib.Path, content: str):
        with open(os.path.join(str(directory), "config.ini"), "w") as text_file:
            text_file.write(content)

    def test_get_contacts(self):
        self.assertEqual(
            ["a@test.com"],
            self._cfg.get_contacts_notified_on_job_failure_user_error(),
        )
        self.assertEqual(
            ["b@test.com", "asdf"],
            self._cfg.get_contacts_notified_on_job_failure_platform_error(),
        )
        self.assertEqual(
            ["c1@test.com", "c2@test.com"],
            self._cfg.get_contacts_notified_on_job_success(),
        )
        self.assertEqual([], self._cfg.get_contacts_notified_on_job_deploy())

    def test_get_team(self):
        self.assertEqual("foo", self._cfg.get_team())

    def test_get_enable_attempt_notifications(self):
        self.assertEqual(True, self._cfg.get_enable_attempt_notifications())

    def test_get_db_default_type(self):
        self.assertEqual("IMPALA", self._cfg.get_db_type())

    def test_get_contacts_not_specified(self):
        self._write_to_config_ini(self._test_dir, "")
        cfg = JobConfig(self._test_dir)
        self.assertEqual([], cfg.get_contacts_notified_on_job_failure_user_error())
        self.assertEqual([], cfg.get_contacts_notified_on_job_failure_platform_error())
        self.assertEqual([], cfg.get_contacts_notified_on_job_success())
        self.assertEqual([], cfg.get_contacts_notified_on_job_deploy())

    def test_defaults(self, tmpdir):
        empty_file_dir = tmpdir.mkdir("foo")
        empty_file = os.path.join(empty_file_dir, "config.ini")
        open(empty_file, "a").close()
        cfg = JobConfig(pathlib.Path(empty_file_dir))

        self.assertEqual(False, cfg.get_enable_attempt_notifications())
        # this is the only important default no need to verify the others.

    def test_vdk_options_empty(self):
        self.assertEqual({}, self._cfg.get_vdk_options())

    def test_vdk_options(self):
        self._write_to_config_ini(
            self._test_dir,
            """
            [vdk]
            a=b
        """,
        )
        cfg = JobConfig(self._test_dir)
        self.assertEqual({"a": "b"}, cfg.get_vdk_options())

    def test_set_team(self):
        self._perform_set_team_test("my_unique_team_name")

    def test_set_empty_team(self):
        self._perform_set_team_test("")

    def test_set_team_with_spaces(self):
        self._perform_set_team_test("my unique team name")

    def test_set_team_with_no_team_in_config_ini(self):
        # remove all contents of config.ini (including team option)
        self._write_to_config_ini(
            self._test_dir,
            """
            """,
        )
        cfg = JobConfig(self._test_dir)

        assert not cfg.get_team(), f"empty config.ini file should not provide a team"

        assert not cfg.set_team_if_exists(
            "my unique team name"
        ), f"set_team_if_exists was supposed to return False if there is no team option in config.ini"

    def _perform_set_team_test(self, team_name):
        assert self._cfg.set_team_if_exists(
            team_name
        ), f"team option was expected to be present in: {self._test_config_path}"

        with open(self._test_config_path) as f:
            assert (
                team_name in f.read()
            ), f"set_team_if_exists failed to write team {team_name} in: {self._test_config_path}"

    def test_notification_delay_period_minutes(self):
        self.__create_job_config_with_custom_contacts(
            [("notification_delay_period_minutes", "100")],
        )
        job_config = JobConfig(self._test_dir)
        assert job_config.get_notification_delay_period_minutes() == 100

    def test_invalid_notification_delay_period_minutes(self):
        self.__create_job_config_with_custom_contacts(
            [("notification_delay_period_minutes", "invalid_value")],
        )
        job_config = JobConfig(self._test_dir)
        with pytest.raises(VdkConfigurationError):
            job_config.get_notification_delay_period_minutes()

    def test_negative_notification_delay_period_minutes(self):
        self.__create_job_config_with_custom_contacts(
            [("notification_delay_period_minutes", "-100")],
        )
        job_config = JobConfig(self._test_dir)
        with pytest.raises(VdkConfigurationError):
            job_config.get_notification_delay_period_minutes()

    def test_parse_notification_contacts(self):
        self.__create_job_config_with_custom_contacts(
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
        job_config = JobConfig(self._test_dir)
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

    def __create_job_config_with_custom_contacts(self, contacts):
        # remove all contents of config.ini (including team option)
        self._write_to_config_ini(
            self._test_dir,
            """
            """,
        )
        config = configparser.ConfigParser()
        config.add_section("contacts")
        for k, v in contacts:
            config.set("contacts", k, v)
        with open(self._test_config_path, "w") as f:
            config.write(f)

    @staticmethod
    def assertEqual(lhs, rhs):
        assert lhs == rhs
