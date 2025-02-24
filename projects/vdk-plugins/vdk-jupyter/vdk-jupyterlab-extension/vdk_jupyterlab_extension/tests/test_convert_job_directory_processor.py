# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import tempfile
import unittest

from vdk_jupyterlab_extension.convert_job import ConvertJobDirectoryProcessor


class TestConvertJobDirectoryProcessor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sql_content = "SELECT * FROM table"
        self.py_content_run = """
def run(job_input: IJobInput):
    print("Hello, World!")
        """
        self.py_content_without_run = """
def hello():
    print("Hello, World!")
'''
commented out def run
def run(job_input)
'''
        """
        self.py_content_run_multiline = """
def run(
    job_input: IJobInput
):
    print('Hello, World!')
        """
        self.py_content_run_spaces = """
def run(  job_input: IJobInput):
    print('Hello, World!')
        """
        self.py_content_run_in_a_class = """
class X:
    def run(job_input: IJobInput):
        print("Hello, World!")
        """

        with open(os.path.join(self.temp_dir, "10_test.sql"), "w") as f:
            f.write(self.sql_content)
        with open(os.path.join(self.temp_dir, "20_test_run.py"), "w") as f:
            f.write(self.py_content_run)
        with open(os.path.join(self.temp_dir, "30_test_without_run.py"), "w") as f:
            f.write(self.py_content_without_run)
        with open(os.path.join(self.temp_dir, "40_test_multi_line_run.py"), "w") as f:
            f.write(self.py_content_run_multiline)
        with open(os.path.join(self.temp_dir, "50_test_spaces.py"), "w") as f:
            f.write(self.py_content_run_spaces)
        with open(os.path.join(self.temp_dir, "60_run_in_a_class.py"), "w") as f:
            f.write(self.py_content_run_in_a_class)
        with open(os.path.join(self.temp_dir, "config.ini"), "w") as f:
            pass

        self.processor = ConvertJobDirectoryProcessor(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_process_non_step_files_remain(self):
        self.processor.process_files()
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, "30_test_without_run.py"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, "60_run_in_a_class.py"))
        )
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "config.ini")))

    def test_cleanup(self):
        self.processor.process_files()
        self.processor.cleanup()
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, "10_test.sql")))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, "20_test_run.py")))
        self.assertFalse(
            os.path.exists(os.path.join(self.temp_dir, "40_test_multi_line_run.py"))
        )
        self.assertFalse(
            os.path.exists(os.path.join(self.temp_dir, "50_test_spaces.py"))
        )

        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, "30_test_without_run.py"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_dir, "60_run_in_a_class.py"))
        )
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "config.ini")))

    def test_get_code_structure(self):
        self.processor.process_files()
        expected_code_structure = [
            f"%%vdksql\n{self.sql_content}",
            self.py_content_run,
            self.py_content_run_multiline,
            self.py_content_run_spaces,
        ]
        self.assertEqual(self.processor.get_code_structure(), expected_code_structure)

    def test_get_removed_files(self):
        self.processor.process_files()
        expected_removed_files = [
            "10_test.sql",
            "20_test_run.py",
            "40_test_multi_line_run.py",
            "50_test_spaces.py",
        ]
        self.assertEqual(
            set(self.processor.get_removed_files()), set(expected_removed_files)
        )

    def test_get_bad_python_file(self):
        bad_job_dir = tempfile.mkdtemp()
        try:
            py_content_with_incorrect_syntax = """
    def run(job_input: IJobInput

        print(' Hello, World!')
            """
            with open(os.path.join(bad_job_dir, "50_test_spaces.py"), "w") as f:
                f.write(py_content_with_incorrect_syntax)
            processor = ConvertJobDirectoryProcessor(bad_job_dir)

            try:
                processor.process_files()
                assert False, "Expected SyntaxError exception"
            except SyntaxError as e:
                assert "50_test_spaces.py" in e.filename
        finally:
            shutil.rmtree(bad_job_dir)
