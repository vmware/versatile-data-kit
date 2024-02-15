# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import re

from vdk.internal.core import errors


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


def set_non_root_log_levels(vdk_log_level: str, log_level_module: str):
    logging.getLogger("requests_kerberos").setLevel(logging.INFO)
    logging.getLogger("requests_oauthlib").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)
    logging.getLogger("vdk").setLevel(vdk_log_level)

    parsed_log_levels = parse_log_level_module(log_level_module)
    for logger_name, level_info in parsed_log_levels.items():
        logging.getLogger(logger_name).setLevel(level_info["level"])
