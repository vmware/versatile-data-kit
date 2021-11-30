# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""This module contains the logic that
decides who is to blame, between Platform (SRE) Team and VDK Users,
when an exception occurs while executing a Data Job step.
"""
import os
import traceback
from pathlib import Path
from typing import Optional

from vdk.internal.core import errors


def whom_to_blame(exception, executor_module, data_job_path: Optional[Path] = None):
    """
    :param exception: Exception object that has led to Data Job failure.
    :param executor_module: name of module that executes User Code.
    :param data_job_path: path object of the data job directory.
    :return: ResolvableBy.PLATFORM_ERROR if exception was recognized as Platform Team responsibility.
             errors.ResolvableBy.USER_ERROR if exception was recognized as User Error.
    """
    if isinstance(exception, errors.BaseVdkError):
        return errors.find_whom_to_blame_from_exception(exception)
    if is_user_error(exception, data_job_path):
        return errors.ResolvableBy.USER_ERROR
    if _is_exception_from_vdk_code(
        exception, executor_module
    ):  # We want to avoid blaming users for errors raised from VDK code
        return (
            errors.ResolvableBy.PLATFORM_ERROR
        )  # Because we can't be 100% sure if they are user errors
    else:
        return errors.ResolvableBy.USER_ERROR


def _is_exception_from_vdk_code(exception, executor_module):
    executor_module = os.path.abspath(executor_module)
    vdk_code_directory = os.path.dirname(executor_module)
    call_list = traceback.format_tb(exception.__traceback__)
    call_list.reverse()  # First element is most recent call
    if len(call_list) == 0:
        return True

    for call in call_list:
        caller_module = call.split('"')[1]  # Extract module path from stacktrace call.
        if vdk_code_directory in caller_module and caller_module != executor_module:
            return True
        elif (
            caller_module == executor_module
        ):  # User code starts from this module always.
            break

    return False


def is_user_error(
    received_exception: Exception, data_job_path: Optional[Path] = None
) -> bool:
    """
    Returns if exception should be user error
    """
    return (
        _is_file_size_limit_exceeded(received_exception)
        or _is_new_thread_error(received_exception)
        or _is_timeout_error(received_exception)
        or _is_memory_limit_exceeded(received_exception)
        or _is_direct_user_code_error(received_exception, job_path=data_job_path)
    )


def _is_memory_limit_exceeded(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="MemoryError",
        exception_message_matcher_regex=".*",
    )


def _is_file_size_limit_exceeded(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="OSError",
        exception_message_matcher_regex=".*File size limit.*",
    )


def _is_new_thread_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="RuntimeError",
        exception_message_matcher_regex=".*new thread.*",
    )


def _is_timeout_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package=".*TimeoutError.*",
        exception_message_matcher_regex=".*Duration of Data Job exceeded.*seconds.*",
    )


def _is_direct_user_code_error(exception: Exception, job_path: Optional[Path]):
    data_job_path = str(job_path) if job_path else None
    if not data_job_path:
        return False

    # Get exception traceback as a list
    call_list = traceback.format_tb(exception.__traceback__)
    if len(call_list) == 0:
        return False

    last_call = call_list[-1]
    last_caller_module = last_call.split('"')[1]

    # Check if the data job path is contained in the last exception call from the exception
    # traceback. If it is, it is safe to assume that the exception was generated directly in
    # user code, and not somewhere else in the vdk code or one of vdk's plugins.
    return True if data_job_path in last_caller_module else False
