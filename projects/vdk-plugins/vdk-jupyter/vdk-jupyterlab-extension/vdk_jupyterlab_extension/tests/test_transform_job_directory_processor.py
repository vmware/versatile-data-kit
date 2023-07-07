import os
import unittest
import tempfile
import shutil
from vdk_jupyterlab_extension.transform_job import TransformJobDirectoryProcessor


class TestTransformJobDirectoryProcessor(unittest.TestCase):
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
        """

        with open(os.path.join(self.temp_dir, 'test.sql'), 'w') as f:
            f.write(self.sql_content)
        with open(os.path.join(self.temp_dir, 'test_run.py'), 'w') as f:
            f.write(self.py_content_run)
        with open(os.path.join(self.temp_dir, 'test_without_run.py'), 'w') as f:
            f.write(self.py_content_without_run)
        with open(os.path.join(self.temp_dir, 'config.ini'), 'w') as f:
            pass

        self.processor = TransformJobDirectoryProcessor(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_process_files(self):
        self.processor.process_files()
        expected_code_structure = [
            f'job_input.execute_query("""{self.sql_content}""")',
            self.py_content_run,
        ]
        self.assertEqual(self.processor.get_code_structure(), expected_code_structure)
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, 'test.sql')))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, 'test_run.py')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'test_without_run.py')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'config.ini')))

    def test_get_code_structure(self):
        self.processor.process_files()
        expected_code_structure = [
            f'job_input.execute_query("""{self.sql_content}""")',
            self.py_content_run,
        ]
        self.assertEqual(self.processor.get_code_structure(), expected_code_structure)
