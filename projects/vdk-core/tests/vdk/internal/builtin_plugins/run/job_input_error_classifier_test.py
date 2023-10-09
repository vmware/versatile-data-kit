# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from vdk.internal.builtin_plugins.run import data_job
from vdk.internal.builtin_plugins.run.job_input_error_classifier import is_user_error
from vdk.internal.builtin_plugins.run.job_input_error_classifier import whom_to_blame
from vdk.internal.core import errors


class ErrorClassifierTest(unittest.TestCase):
    EXECUTOR_MODULE = data_job.__file__
    EXECUTOR_MODULE_DIR = os.path.dirname(EXECUTOR_MODULE)
    INGESTOR_MODULE_DIR = os.path.dirname(EXECUTOR_MODULE).replace("run", "ingestion")

    PLATFORM_ERROR_EXTERNAL_LIBRARY = [
        """
        File "/opt/homebrew/lib/python3.11/site-packages/pandas/io/parsers/readers.py", line 912, in read_csv
        """,
        """
        File "{}/job_input.py", line 155, in send_tabular_data_for_ingestion
        """.format(
            EXECUTOR_MODULE_DIR
        ),
        """
        File "{}/file_based_step.py", line 139, in invoke_run_function
        """.format(
            EXECUTOR_MODULE_DIR
        ),
        """
        File "{}", line 9, in run
        """.format(
            os.path.join("job", "moonshine-ri", "21-find-ri-optimal.py")
        ),
        """
        File "{}/ingester_router.py", line 142, in send_tabular_data_for_ingestion
        """.format(
            INGESTOR_MODULE_DIR
        ),
    ]

    USER_ERROR_STACKTRACE = [
        """File "{exec_module}", line 123, in _run_step
      step_executed = runner_func(file_path)""".format(
            exec_module=EXECUTOR_MODULE
        ),
        """File "{exec_module}", line 190, in _run_python_step
      func(self.job_input)""".format(
            exec_module=EXECUTOR_MODULE
        ),
        """File "{user_module}", line 111, in run
      raise ValueError('No objects to concatenate')""".format(
            user_module=os.path.join("job", "moonshine-ri", "21_find_ri_optimal.py")
        ),
    ]

    GENERIC_USER_ERROR_STACKTRACE = [
        f""""{EXECUTOR_MODULE}", line 71, in run_step
    step_executed = step.runner_func(step, context.job_input)""",
        f"""File "{EXECUTOR_MODULE_DIR}/file_based_step.py", line 83, in run_python_step
    StepFuncFactory.invoke_run_function(func, job_input)""",
        f"""File "{EXECUTOR_MODULE_DIR}/file_based_step.py", line 117, in invoke_run_function
    func(**actual_arguments)""",
        """File "/example_project/my-second-job/20_python_step.py", line 24, in run
    raise Exception("Some test exception from user code") Exception: Some test exception from user code""",
    ]

    PLATFORM_ERROR_STACKTRACE = [
        """File "{exec_module}", line 133, in _run_step
      step_executed = runner_func(file_path)""".format(
            exec_module=EXECUTOR_MODULE
        ),
        """File "{exec_module}", line 199, in _run_python_step
      func(self.job_input)""".format(
            exec_module=EXECUTOR_MODULE
        ),
        """File "{user_module}", line 2, in run
      job_input.load_csv('/home/pmitev/csv_files/no_read', 'random')""".format(
            user_module=os.path.join("home", "pmitev", "test-job", "10_load.py")
        ),
        """File "{vdk_file}", line 77, in load_csv
      raise ValueError('Test VAC Error')""".format(
            vdk_file=os.path.join(EXECUTOR_MODULE_DIR, "job_input.py")
        ),
    ]

    # Test VDK specific errors.
    def test_vdk_user_code_error(self):
        exception = errors.UserCodeError("User error")
        self.assertEqual(
            errors.ResolvableBy.USER_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )

    def test_vdk_platform_service_error(self):
        exception = errors.PlatformServiceError("Platform error")
        self.assertEqual(
            errors.ResolvableBy.PLATFORM_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )

    # Test generic errors specifically recognised as user errors by VDK.
    @patch(f"{is_user_error.__module__}.{is_user_error.__name__}")
    def test_known_generic_error(self, mock_is_user_error):
        mock_is_user_error.return_value = True
        exception = Exception("User Error")
        self.assertEqual(
            errors.ResolvableBy.USER_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )

    # Test generic errors that are not specifically recognised by VDK.
    @patch(f"{traceback.format_tb.__module__}.{traceback.format_tb.__name__}")
    @patch(f"{is_user_error.__module__}.{is_user_error.__name__}")
    def test_unknown_generic_error(self, mock_is_user_error, mock_traceback_format_tb):
        exception = Exception("User Error")
        mock_is_user_error.return_value = False
        mock_traceback_format_tb.return_value = self.USER_ERROR_STACKTRACE
        self.assertEqual(
            errors.ResolvableBy.USER_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )

    # Test generic errors in user code that are not specifically recognised by VDK.
    @patch(f"{traceback.format_tb.__module__}.{traceback.format_tb.__name__}")
    def test_unknown_user_code_error(self, mock_traceback_format_tb):
        data_job_path = Path("/example_project/my-second-job")
        exception = Exception("User Error")

        mock_traceback_format_tb.return_value = self.GENERIC_USER_ERROR_STACKTRACE
        self.assertEqual(
            errors.ResolvableBy.USER_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE, data_job_path),
        )

    # Test errors in user code that cannot be recognised by VDK due to lack of valid job_path.
    @patch(f"{traceback.format_tb.__module__}.{traceback.format_tb.__name__}")
    def test_unknown_user_code_error_with_none_job_path(self, mock_traceback_format_tb):
        data_job_path = None
        exception = Exception("Should be Platform Error")

        mock_traceback_format_tb.return_value = self.GENERIC_USER_ERROR_STACKTRACE
        self.assertEqual(
            errors.ResolvableBy.PLATFORM_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE, data_job_path),
        )

    # Test errors thrown from external libraries used by vdk internal components
    @patch(f"{traceback.format_tb.__module__}.{traceback.format_tb.__name__}")
    def test_error_thrown_in_external_library(self, mock_traceback_format_tb):
        exception = Exception("Should be Platform Error")
        print(self.EXECUTOR_MODULE)
        mock_traceback_format_tb.return_value = self.PLATFORM_ERROR_EXTERNAL_LIBRARY
        self.assertEqual(
            errors.ResolvableBy.PLATFORM_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )

    # Generic error thrown by job_input that is not specifically recognised by VDK should be VAC error.
    @patch(f"{traceback.format_tb.__module__}.{traceback.format_tb.__name__}")
    @patch(f"{is_user_error.__module__}.{is_user_error.__name__}")
    def test_job_input_generic_error(
        self, mock_is_user_error, mock_traceback_format_tb
    ):
        exception = Exception("!")
        mock_is_user_error.return_value = False
        mock_traceback_format_tb.return_value = self.PLATFORM_ERROR_STACKTRACE
        self.assertEqual(
            errors.ResolvableBy.PLATFORM_ERROR,
            whom_to_blame(exception, self.EXECUTOR_MODULE),
        )


class UserErrorClassification(unittest.TestCase):
    def test_user_error_classification(self):
        self.assertTrue(
            is_user_error(
                OSError(
                    "File size limit (10 MB) for Data Job has been exceeded.Optimize the disk utilization of your Data Job."
                    "For local runs this limit can be changed by 'export VDK_RESOURCE_LIMIT_DISK_MB=<new-value>'.For cloud "
                    "run you can fill in a Service Request (http://go/resource-limits) for the limit to be changed. "
                    "This limit does not apply to macOS and Windows execution environments."
                )
            )
        )
        self.assertTrue(
            is_user_error(
                RuntimeError(
                    "Unable to start new thread. Optimize thread usage of your Data Job."
                )
            )
        )
        self.assertTrue(is_user_error(MemoryError("foo")))
