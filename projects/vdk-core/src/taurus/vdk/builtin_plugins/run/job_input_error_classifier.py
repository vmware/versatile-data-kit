# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""This module contains the logic that
decides who is to blame, between Platform (SRE) Team and VDK Users,
when an exception occurs while executing a Data Job step.
"""
import os
import traceback

from taurus.vdk.core import errors


def whom_to_blame(exception, executor_module):
    """
    :param exception: Exception object that has led to Data Job failure.
    :param executor_module: name of module that executes User Code.
    :return: ResolvableBy.PLATFORM_ERROR if exception was recognized as Platform Team responsibility.
             errors.ResolvableBy.USER_ERROR if exception was recognized as User Error.
    """
    if isinstance(exception, errors.BaseVdkError):
        return errors.find_whom_to_blame_from_exception(exception)
    if is_user_error(exception):
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


def is_user_error(received_exception: Exception) -> bool:
    """
    Returns if exception should be user error
    """
    return (
        _is_file_size_limit_exceeded(received_exception)
        or _is_new_thread_error(received_exception)
        or _is_timeout_error(received_exception)
        or _is_memory_limit_exceeded(received_exception)
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
