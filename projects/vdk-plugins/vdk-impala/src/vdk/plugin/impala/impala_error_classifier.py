# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core import errors


def is_impala_user_error(received_exception):
    if errors.exception_matches(
        received_exception,
        classname_with_package="impala.error.HiveServer2Error",
        exception_message_matcher_regex="^AnalysisException: This Impala daemon is not ready to accept user requests.*",
    ):
        return False

    return (
        _is_syntax_error(received_exception)
        or _is_udf_error(received_exception)
        or _is_authorization_error(received_exception)
        or _is_query_limit_exceeded(received_exception)
        or _is_impala_memory_limit_exceeded(received_exception)
        or _is_quota_exceeded(received_exception)
        or _is_other_query_error(received_exception)
        or _is_property_unsupported_value_error(received_exception)
    )


def _is_syntax_error(exception):
    return (
        errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex="^AnalysisException.*",
        )
        or errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex="^ParseException: Syntax error.*",
        )
        or errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex="^Could not compile regexp pattern.*",
        )
        or errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex="^TableNotFoundException.*",
        )
        or errors.exception_matches(
            exception,
            classname_with_package="impala.error.HiveServer2Error",
            exception_message_matcher_regex=".*ArrayIndexOutOfBoundsException:.*",
        )
    )


def _is_udf_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="impala.error.OperationalError",
        exception_message_matcher_regex="^UDF ERROR:.*",
    )


def _is_authorization_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="impala.error.HiveServer2Error",
        exception_message_matcher_regex="^AuthorizationException:.*",
    )


def _is_query_limit_exceeded(exception):
    return (
        # Error specified below occurs when query exceeds 1h time limit
        errors.exception_matches(
            exception,
            classname_with_package="impala.error.OperationalError",
            exception_message_matcher_regex="^Cancelled from Impala's debug web interface$",
        )
        or errors.exception_matches(
            exception,
            classname_with_package="impala.error.OperationalError",
            exception_message_matcher_regex="^.*expired due to execution time limit.*$",
        )
    )


def _is_other_query_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="impala.error.OperationalError",
        exception_message_matcher_regex=".*Cannot perform hash join at node with id.*",
    )


def _is_property_unsupported_value_error(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="ValueError",
        exception_message_matcher_regex=".*[pP]roperty.*is of unsupported type.*",
    )


def _is_impala_memory_limit_exceeded(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="impala.error.OperationalError",
        exception_message_matcher_regex=".*Scratch space limit.*",
    ) or errors.exception_matches(
        exception,
        classname_with_package="impala.error.OperationalError",
        exception_message_matcher_regex=".*Memory limit exceeded.*",
    )


def _is_quota_exceeded(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="impala.error.OperationalError",
        exception_message_matcher_regex=".*DiskSpace quota of .* is exceeded.*",
    )
