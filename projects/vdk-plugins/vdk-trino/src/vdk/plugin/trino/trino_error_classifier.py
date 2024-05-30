# Copyright 2024-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core import errors


def is_trino_user_error(received_exception):
    return (
        _is_user_error(received_exception)
        or _is_internal_error(received_exception)
        or _is_resource_error(received_exception)
        or _is_query_time_exceeded(received_exception)
    )


def _is_user_error(exception):
    user_error_list = [
        "GENERIC_USER_ERROR",
        "SYNTAX_ERROR",
        "ABANDONED_QUERY",
        "USER_CANCELED",
        "PERMISSION_DENIED",
        "NOT_FOUND",
        "FUNCTION_NOT_FOUND",
        "INVALID_FUNCTION_ARGUMENT",
        "DIVISION_BY_ZERO",
        "INVALID_CAST_ARGUMENT",
        "OPERATOR_NOT_FOUND",
        "INVALID_VIEW",
        "ALREADY_EXISTS",
        "NOT_SUPPORTED",
        "INVALID_SESSION_PROPERTY",
        "INVALID_WINDOW_FRAME",
        "CONSTRAINT_VIOLATION",
        "TRANSACTION_CONFLICT",
        "INVALID_TABLE_PROPERTY",
        "NUMERIC_VALUE_OUT_OF_RANGE",
        "UNKNOWN_TRANSACTION",
        "NOT_IN_TRANSACTION",
        "TRANSACTION_ALREADY_ABORTED",
        "READ_ONLY_VIOLATION",
        "MULTI_CATALOG_WRITE_CONFLICT",
        "AUTOCOMMIT_WRITE_CONFLICT",
        "UNSUPPORTED_ISOLATION_LEVEL",
        "INCOMPATIBLE_CLIENT",
        "SUBQUERY_MULTIPLE_ROWS",
        "PROCEDURE_NOT_FOUND",
        "INVALID_PROCEDURE_ARGUMENT",
        "QUERY_REJECTED",
        "AMBIGUOUS_FUNCTION_CALL",
        "INVALID_SCHEMA_PROPERTY",
        "SCHEMA_NOT_EMPTY",
        "QUERY_TEXT_TOO_LARGE",
        "UNSUPPORTED_SUBQUERY",
        "EXCEEDED_FUNCTION_MEMORY_LIMIT",
        "ADMINISTRATIVELY_KILLED",
        "INVALID_COLUMN_PROPERTY",
        "QUERY_HAS_TOO_MANY_STAGES",
        "INVALID_SPATIAL_PARTITIONING",
        "INVALID_ANALYZE_PROPERTY",
        "TYPE_NOT_FOUND",
        "CATALOG_NOT_FOUND",
        "SCHEMA_NOT_FOUND",
        "TABLE_NOT_FOUND",
        "COLUMN_NOT_FOUND",
        "ROLE_NOT_FOUND",
        "SCHEMA_ALREADY_EXISTS",
        "TABLE_ALREADY_EXISTS",
        "COLUMN_ALREADY_EXISTS",
        "ROLE_ALREADY_EXISTS",
        "DUPLICATE_NAMED_QUERY",
        "DUPLICATE_COLUMN_NAME",
        "MISSING_COLUMN_NAME",
        "MISSING_CATALOG_NAME",
        "MISSING_SCHEMA_NAME",
        "TYPE_MISMATCH",
        "INVALID_LITERAL",
        "COLUMN_TYPE_UNKNOWN",
        "MISMATCHED_COLUMN_ALIASES",
        "AMBIGUOUS_NAME",
        "INVALID_COLUMN_REFERENCE",
        "MISSING_GROUP_BY",
        "MISSING_ORDER_BY",
        "MISSING_OVER",
        "NESTED_AGGREGATION",
        "NESTED_WINDOW",
        "EXPRESSION_NOT_IN_DISTINCT",
        "TOO_MANY_GROUPING_SETS",
        "FUNCTION_NOT_WINDOW",
        "FUNCTION_NOT_AGGREGATE",
        "EXPRESSION_NOT_AGGREGATE",
        "EXPRESSION_NOT_SCALAR",
        "EXPRESSION_NOT_CONSTANT",
        "INVALID_ARGUMENTS",
        "TOO_MANY_ARGUMENTS",
        "INVALID_PRIVILEGE",
        "DUPLICATE_PROPERTY",
        "INVALID_PARAMETER_USAGE",
        "VIEW_IS_STALE",
        "VIEW_IS_RECURSIVE",
        "NULL_TREATMENT_NOT_ALLOWED",
        "INVALID_ROW_FILTER",
        "INVALID_COLUMN_MASK",
        "MISSING_TABLE",
        "INVALID_RECURSIVE_REFERENCE",
        "MISSING_COLUMN_ALIASES",
        "NESTED_RECURSIVE",
        "INVALID_LIMIT_CLAUSE",
        "INVALID_ORDER_BY",
        "DUPLICATE_WINDOW_NAME",
        "INVALID_WINDOW_REFERENCE",
        "INVALID_PARTITION_BY",
        "INVALID_MATERIALIZED_VIEW_PROPERTY",
        "INVALID_LABEL",
        "INVALID_PROCESSING_MODE",
        "INVALID_NAVIGATION_NESTING",
        "INVALID_ROW_PATTERN",
        "NESTED_ROW_PATTERN_RECOGNITION",
        "TABLE_HAS_NO_COLUMNS",
        "INVALID_RANGE",
        "INVALID_PATTERN_RECOGNITION_FUNCTION",
        "TABLE_REDIRECTION_ERROR",
        "MISSING_VARIABLE_DEFINITIONS",
        "MISSING_ROW_PATTERN",
        "INVALID_WINDOW_MEASURE",
        "STACK_OVERFLOW",
        "MISSING_RETURN_TYPE",
        "AMBIGUOUS_RETURN_TYPE",
        "MISSING_ARGUMENT",
        "DUPLICATE_PARAMETER_NAME",
        "INVALID_PATH",
        "JSON_INPUT_CONVERSION_ERROR",
        "JSON_OUTPUT_CONVERSION_ERROR",
        "PATH_EVALUATION_ERROR",
        "INVALID_JSON_LITERAL",
        "JSON_VALUE_RESULT_ERROR",
        "MERGE_TARGET_ROW_MULTIPLE_MATCHES",
        "INVALID_COPARTITIONING",
        "INVALID_TABLE_FUNCTION_INVOCATION",
        "DUPLICATE_RANGE_VARIABLE",
        "INVALID_CHECK_CONSTRAINT",
        "INVALID_CATALOG_PROPERTY",
        "CATALOG_UNAVAILABLE",
        "MISSING_RETURN",
        "DUPLICATE_COLUMN_OR_PATH_NAME",
        "MISSING_PATH_NAME",
        "INVALID_PLAN",
        "INVALID_VIEW_PROPERTY",
        "UNSUPPORTED_TABLE_TYPE",
    ]
    for error in user_error_list:
        flag = errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex=f".*{error}.*",
        )
        if flag:
            return True
    return False


def _is_internal_error(exception):
    internal_error_list = [
        "GENERIC_INTERNAL_ERROR",
        "TOO_MANY_REQUESTS_FAILED",
        "PAGE_TOO_LARGE",
        "PAGE_TRANSPORT_ERROR",
        "PAGE_TRANSPORT_TIMEOUT",
        "NO_NODES_AVAILABLE",
        "REMOTE_TASK_ERROR",
        "COMPILER_ERROR",
        "REMOTE_TASK_MISMATCH",
        "SERVER_SHUTTING_DOWN",
        "FUNCTION_IMPLEMENTATION_MISSING",
        "REMOTE_BUFFER_CLOSE_FAILED",
        "SERVER_STARTING_UP",
        "FUNCTION_IMPLEMENTATION_ERROR",
        "INVALID_PROCEDURE_DEFINITION",
        "PROCEDURE_CALL_FAILED",
        "AMBIGUOUS_FUNCTION_IMPLEMENTATION",
        "ABANDONED_TASK",
        "CORRUPT_SERIALIZED_IDENTITY",
        "CORRUPT_PAGE",
        "OPTIMIZER_TIMEOUT",
        "OUT_OF_SPILL_SPACE",
        "REMOTE_HOST_GONE",
        "CONFIGURATION_INVALID",
        "CONFIGURATION_UNAVAILABLE",
        "INVALID_RESOURCE_GROUP",
        "SERIALIZATION_ERROR",
        "REMOTE_TASK_FAILED",
        "EXCHANGE_MANAGER_NOT_CONFIGURED",
        "CATALOG_NOT_AVAILABLE",
        "CATALOG_STORE_ERROR",
    ]
    for error in internal_error_list:
        flag = errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex=f".*{error}.*",
        )
        if flag:
            return True
    return False


def _is_resource_error(exception):
    resource_error_list = [
        "GENERIC_INSUFFICIENT_RESOURCES",
        "EXCEEDED_GLOBAL_MEMORY_LIMIT",
        "QUERY_QUEUE_FULL",
        "EXCEEDED_TIME_LIMIT",
        "CLUSTER_OUT_OF_MEMORY",
        "EXCEEDED_CPU_LIMIT",
        "EXCEEDED_SPILL_LIMIT",
        "EXCEEDED_LOCAL_MEMORY_LIMIT",
        "ADMINISTRATIVELY_PREEMPTED",
        "EXCEEDED_SCAN_LIMIT",
        "EXCEEDED_TASK_DESCRIPTOR_STORAGE_CAPACITY",
    ]
    for error in resource_error_list:
        flag = errors.exception_matches(
            exception,
            classname_with_package="trino.exceptions.TrinoException",
            exception_message_matcher_regex=f".*{error}.*",
        )
        if flag:
            return True
    return False


def _is_query_time_exceeded(exception):
    return errors.exception_matches(
        exception,
        classname_with_package="trino.exceptions.TrinoException",
        exception_message_matcher_regex="^TIMEOUT.*",
    )
