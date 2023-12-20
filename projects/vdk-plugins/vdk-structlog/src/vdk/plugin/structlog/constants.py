# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

STRUCTLOG_LOGGING_METADATA_KEY = "logging_metadata"
STRUCTLOG_LOGGING_FORMAT_KEY = "logging_format"
STRUCTLOG_CONSOLE_LOG_PATTERN = "logging_custom_format"

STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES = ["console", "json"]
STRUCTLOG_LOGGING_FORMAT_DEFAULT = "console"

STRUCTLOG_LOGGING_METADATA_JOB = {
    "vdk_job_name": "%(vdk_job_name)s",
    "vdk_step_name": "%(vdk_step_name)s",
    "vdk_step_type": "%(vdk_step_type)s",
}

STRUCTLOG_METADATA_FIELDS = {
    "timestamp": "created",
    "level": "levelname",
    "logger_name": "name",
    "file_name": "filename",
    "line_number": "lineno",
    "function_name": "funcName",
}

JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT = {
    "timestamp": "%(created)s",
    "level": "%(levelname)s",
    "logger_name": "%(name)s",
    "file_name": "%(filename)s",
    "line_number": "%(lineno)s",
    "function_name": "%(funcName)s",
}

CONSOLE_STRUCTLOG_LOGGING_METADATA_DEFAULT = {
    "timestamp": "%(asctime)s [VDK]",
    "level": "[%(levelname)-5.5s]",
    "logger_name": "%(name)-30.30s",
    "file_name": "%(filename)20.20s",
    "line_number": ":%(lineno)-4.4s",
    "function_name": "%(funcName)-16.16s",
}

CONSOLE_STRUCTLOG_LOGGING_METADATA_JOB = {
    "vdk_job_name": "%(vdk_job_name)s",
    "vdk_step_name": "%(vdk_step_name)s",
    "vdk_step_type": "%(vdk_step_type)s",
}

CONSOLE_STRUCTLOG_LOGGING_METADATA_ALL = {
    **CONSOLE_STRUCTLOG_LOGGING_METADATA_DEFAULT,
    **CONSOLE_STRUCTLOG_LOGGING_METADATA_JOB,
}

STRUCTLOG_LOGGING_METADATA_ALL = {
    **JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT,
    **STRUCTLOG_LOGGING_METADATA_JOB,
}

STRUCTLOG_LOGGING_METADATA_ALL_KEYS = set(
    JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT.keys()
) | set(STRUCTLOG_LOGGING_METADATA_JOB.keys())

RECORD_DEFAULT_FIELDS = set(vars(logging.LogRecord("", "", "", "", "", "", "")))
