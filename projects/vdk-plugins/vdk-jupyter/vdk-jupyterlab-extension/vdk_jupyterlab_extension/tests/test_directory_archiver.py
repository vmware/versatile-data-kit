# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import tempfile
import unittest

from vdk_jupyterlab_extension.convert_job import DirectoryArchiver


class TestDirectoryArchiver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.archiver = DirectoryArchiver(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_parent_dir(self):
        self.assertEqual(self.archiver.get_parent_dir(), os.path.dirname(self.temp_dir))

    def test_get_archive_name(self):
        dir_name = os.path.basename(self.temp_dir)
        parent_dir = os.path.dirname(self.temp_dir)
        expected_archive_name = os.path.join(parent_dir, f"{dir_name}_archive")
        self.assertEqual(self.archiver._get_archive_name(), expected_archive_name)

    def test_archive_folder(self):
        self.archiver.archive_folder()
        archive_name = self.archiver._get_archive_name()
        self.assertTrue(os.path.exists(f"{archive_name}.zip"))
