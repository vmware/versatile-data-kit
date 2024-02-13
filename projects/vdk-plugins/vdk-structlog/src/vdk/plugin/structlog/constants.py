# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import socket

STRUCTLOG_USE_STRUCTLOG = "use_structlog"
STRUCTLOG_LOGGING_METADATA_KEY = "structlog_metadata"
STRUCTLOG_LOGGING_FORMAT_KEY = "structlog_format"
STRUCTLOG_CONSOLE_LOG_PATTERN = "structlog_console_custom_format"
STRUCTLOG_CONFIG_PRESET = "structlog_config_preset"
STRUCTLOG_FORMAT_INIT_LOGS = "structlog_format_init_logs"

STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES = ["console", "json", "ltsv"]
STRUCTLOG_LOGGING_FORMAT_DEFAULT = "console"

STRUCTLOG_LOGGING_METADATA_JOB = {
    "attempt_id": "%(attempt_id)s",
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
    "attempt_id": "[id:%(attempt_id)s]",
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

# Syslog constants
SYSLOG_HOST_KEY = "syslog_host"
SYSLOG_PORT_KEY = "syslog_port"
SYSLOG_PROTOCOL_KEY = "syslog_protocol"
SYSLOG_ENABLED_KEY = "syslog_enabled"

# Default values for Syslog
DEFAULT_SYSLOG_HOST = "localhost"
DEFAULT_SYSLOG_PORT = 514
DEFAULT_SYSLOG_PROTOCOL = "UDP"
DEFAULT_SYSLOG_ENABLED = False

SYSLOG_PROTOCOLS = {"UDP": socket.SOCK_DGRAM, "TCP": socket.SOCK_STREAM}

DETAILED_LOGGING_FORMAT = (
    "%(asctime)s [VDK] %(vdk_job_name)s [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
    "lineno)-4.4s %(funcName)-16.16s[id:%(attempt_id)s]- %(message)s"
)
