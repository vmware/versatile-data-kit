"""
Reporter class used to track and report on test cases.
It use junit xml reporting format.

It's "singleton" type of module - all methods decorated with TestDecorator will be tracked.
And when called report_results it will report current results to stderr or optionally to a file.
"""

import sys

import functools
import time
from junit_xml import TestCase, TestSuite, to_xml_report_string, to_xml_report_file
from taurus.vdk.heartbeat.config import Config
from typing import List


class _Result:
    test_cases: List[TestCase] = []


class TestDecorator:
    """
    Test Decorator used to mark a method as a test. It will track the result of the
    method - It passes if it returns successfully and fails if it raises an exception.
    """
    def __init__(self, name=None):
        self.__name = name

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            error = None
            name = self.__name if self.__name else fn.__qualname__
            start = time.time()
            try:
                result = fn(*args, **kwargs)
                return result
            except BaseException as ex:
                error = ex
                raise
            finally:
                case = TestCase(name, elapsed_sec=time.time() - start)
                if error:
                    case.add_failure_info(message=f"{error}")
                _Result.test_cases.append(case)

        return decorated


def report_results(config: Config):
    ts = TestSuite("VDK Heartbeat Test", _Result.test_cases)

    print(to_xml_report_string([ts]), file=sys.stderr)
    if config.report_junit_xml_file_path:
        with open(config.report_junit_xml_file_path, "w") as file_handle:
            to_xml_report_file(file_handle, [ts])