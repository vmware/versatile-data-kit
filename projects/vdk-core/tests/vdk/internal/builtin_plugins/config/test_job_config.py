# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import shutil
import tempfile

from vdk.internal.builtin_plugins.config.job_config import JobConfig


class TestJobConfig:
    def setup_method(self, method):
        # Create a temporary directory
        self._test_dir = pathlib.Path(tempfile.mkdtemp())
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
        empty_file = os.path.join(empty_file_dir, "empty.ini")
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

    @staticmethod
    def assertEqual(lhs, rhs):
        assert lhs == rhs
