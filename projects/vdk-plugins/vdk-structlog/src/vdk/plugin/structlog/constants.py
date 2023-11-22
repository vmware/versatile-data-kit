# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket

from vdk.internal.core import errors

STRUCTLOG_LOGGING_METADATA_KEY = "logging_metadata"
STRUCTLOG_LOGGING_FORMAT_KEY = "logging_format"

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

SYSLOG_URL = "SYSLOG_URL"
SYSLOG_PORT = "SYSLOG_PORT"
SYSLOG_SOCK_TYPE = "SYSLOG_SOCK_TYPE"
SYSLOG_ENABLED = "SYSLOG_ENABLED"

SYSLOG_SOCK_TYPE_VALUES_DICT = {"UDP": socket.SOCK_DGRAM, "TCP": socket.SOCK_STREAM}


def parse_log_level_module(log_level_module):
    valid_logging_levels = [
        "NOTSET",
        "DEBUG",
        "INFO",
        "WARN",
        "WARNING",
        "ERROR",
        "FATAL",
        "CRITICAL",
    ]
    try:
        if log_level_module and log_level_module.strip():
            modules = log_level_module.split(";")
            result = {}
            for module in modules:
                if module:
                    module_and_level = module.split("=")
                    if not re.search("[a-zA-Z0-9_.-]+", module_and_level[0].lower()):
                        raise ValueError(
                            f"Invalid logging module name: '{module_and_level[0]}'. "
                            f"Must be alphanumerical/underscore characters."
                        )
                    if module_and_level[1].upper() not in valid_logging_levels:
                        raise ValueError(
                            f"Invalid logging level: '{module_and_level[1]}'. Must be one of {valid_logging_levels}."
                        )
                    result[module_and_level[0]] = {"level": module_and_level[1].upper()}
            return result
        else:
            return {}
    except Exception as e:
        errors.report_and_throw(
            errors.VdkConfigurationError(
                "Invalid logging configuration passed to LOG_LEVEL_MODULE.",
                f"Error is: {e}. log_level_module was set to {log_level_module}.",
                "Set correctly configuration to log_level_debug configuration in format 'module=level;module2=level2'",
            )
        )
