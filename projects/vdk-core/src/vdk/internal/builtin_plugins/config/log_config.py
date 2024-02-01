# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import re
import socket
import types
import warnings
from sys import modules
from typing import cast

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.config.vdk_config import LOG_LEVEL_VDK
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.core.statestore import CommonStoreKeys

SYSLOG_URL = "SYSLOG_URL"
SYSLOG_PORT = "SYSLOG_PORT"
SYSLOG_SOCK_TYPE = "SYSLOG_SOCK_TYPE"
SYSLOG_ENABLED = "SYSLOG_ENABLED"

SYSLOG_SOCK_TYPE_VALUES_DICT = {"UDP": socket.SOCK_DGRAM, "TCP": socket.SOCK_STREAM}


def _parse_log_level_module(log_level_module):
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


def configure_initial_logging_before_anything():
    """
    Configure logging at the start of the app.
    At this point we do not know what user has configured so we use some sensible approach
    All logs would be vdk only logs. User code will not have been executed yet so we will use log_level_vdk
    to control the level.
    We default to WARN since in most cases users would not care about internal vdk logs.

    Logging lifecycle:
    1. This function is executed at the entry point of the app and configures default logging format and level
    2. After vdk_initialize hook is executed and CLI command starts then `vdk --verbosity` option is taken (if set)
        and click logging configuration takes over
    3. When initialize_job hook (applicable for vdk run only) is executed then below configure_loggers function
        is run which adds more context to the logs and initializes syslog handler (if configured to do so)
    """
    # TODO uncomment this when the vdk-structlog plugin is released
    # warnings.warn(
    #     "The vdk-core logging configuration is not suitable for production. Please use vdk-structlog instead."
    # )
    log_level = "WARNING"
    if os.environ.get(LOG_LEVEL_VDK, None):
        log_level = os.environ.get(LOG_LEVEL_VDK)
    elif os.environ.get("VDK_LOG_LEVEL_VDK", None):
        log_level = os.environ.get("VDK_LOG_LEVEL_VDK")

    logging.basicConfig(format="%(message)s", level=logging.getLevelName(log_level))


def configure_loggers(
    job_name: str = "",
    attempt_id: str = "no-id",
    log_config_type: str = None,
    vdk_logging_level: str = "DEBUG",
    log_level_module: str = None,
    syslog_args: (str, int, str, bool) = ("localhost", 514, "UDP", False),
) -> None:
    """
    Configure default logging configuration

    :param job_name: the name of the job
    :param attempt_id: the id of the current job run attempt
    :param log_config_type: where the job is executed: CLOUD or LOCAL
    :param vdk_logging_level: The level for vdk specific logs.
    :param log_level_module: The level for modules specific logs
    :param syslog_args: Arguments necessary for SysLog logging.
    """

    import logging.config

    if _is_already_configured():
        log = logging.getLogger(__name__)
        msg = "Logging already configured. This seems like a bug. Fix me!."
        # PLugins would override loggin directly wiht logging library not through this method
        # it is probably OK for tests to configure logging twice. VDK, however, shouldn't.
        log.warning(msg)

    # Likely most logging system (like Log Insight) show the hostname from where the syslog message arrived so no need to include it here.
    DETAILED_FORMAT = (
        f"%(asctime)s [VDK] {job_name} [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
        f"lineno)-4.4s %(funcName)-16.16s[id:{attempt_id}]- %(message)s"
    )

    _LOGGERS = {
        "requests_kerberos": {"level": "INFO"},
        "requests_oauthlib": {"level": "INFO"},
        "urllib3": {"level": "INFO"},
        "vdk": {"level": vdk_logging_level},
    }
    _LOGGERS.update(_parse_log_level_module(log_level_module))

    _FORMATTERS = {"detailedFormatter": {"format": DETAILED_FORMAT}}

    _CONSOLE_HANDLER = {
        "class": "logging.StreamHandler",
        "formatter": "detailedFormatter",
        "stream": "ext://sys.stderr",
    }

    syslog_url, syslog_port, syslog_sock_type, syslog_enabled = syslog_args

    if syslog_sock_type not in SYSLOG_SOCK_TYPE_VALUES_DICT:
        errors.report_and_throw(
            errors.VdkConfigurationError(
                f"Provided configuration variable for {SYSLOG_SOCK_TYPE} has invalid value.",
                f"VDK was run with {SYSLOG_SOCK_TYPE}={syslog_sock_type}, however {syslog_sock_type} is invalid value for this variable.",
                f"Provide a valid value for {SYSLOG_SOCK_TYPE}."
                f"Currently possible values are {list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
            )
        )

    _SYSLOG_HANDLER = {
        "level": "DEBUG",
        "class": "logging.handlers.SysLogHandler",
        "formatter": "detailedFormatter",
        "address": (syslog_url, syslog_port),
        "socktype": SYSLOG_SOCK_TYPE_VALUES_DICT[syslog_sock_type],
        "facility": "user",
    }

    handlers = ["consoleHandler"]
    if syslog_enabled:
        handlers.append("SysLog")

    if "CLOUD" == log_config_type:
        CLOUD = {  # @UnusedVariable
            "version": 1,
            "handlers": {"consoleHandler": _CONSOLE_HANDLER, "SysLog": _SYSLOG_HANDLER},
            "formatters": _FORMATTERS,
            "root": {"handlers": handlers},
            "loggers": _LOGGERS,
            "disable_existing_loggers": False,
        }
        logging.config.dictConfig(CLOUD)
    elif "NONE" == log_config_type:
        pass
    else:
        LOCAL = {  # @UnusedVariable
            "version": 1,
            "handlers": {"consoleHandler": _CONSOLE_HANDLER, "SysLog": _SYSLOG_HANDLER},
            "formatters": _FORMATTERS,
            "root": {"handlers": handlers},
            "loggers": _LOGGERS,
            "disable_existing_loggers": False,
        }
        logging.config.dictConfig(LOCAL)
    _set_already_configured()


def _set_already_configured() -> None:
    setattr(modules[__name__], "logging_already_configured", True)


def _is_already_configured() -> bool:
    res = hasattr(modules[__name__], "logging_already_configured")
    return res


def ensure_logging_for_current_test() -> None:
    """
    To be called from test code only.

    Ensures that logging is configured, either by another class, or by the caller.
    Useful when debugging a single test class, not the whole suite (assuming all suites configure logging)

    Uses filename of caller for derived_dataset parameter, e.g. if this method is called from impala_connection_test.py
    then logs would be configured to look like:

    2018-04-19 16:05:48,488=1524143148[VDK] impala_connection_test.py [DEBUG]  ......
    """
    if not _is_already_configured():
        try:
            from inspect import currentframe

            me = cast(types.FrameType, currentframe())
            caller = cast(types.FrameType, me.f_back)
            path = caller.f_locals["__file__"]
            from os.path import split

            dir, fname = split(path)  # @ReservedAssignment
        except:
            fname = "n/a"
        from time import time

        configure_loggers(fname, str(time()))


class LoggingPlugin:
    """
    Define the logging plugin
    """

    @staticmethod
    @hookimpl
    def vdk_configure(config_builder: ConfigurationBuilder):
        config_builder.add(
            key=SYSLOG_URL,
            default_value="localhost",
            description="The hostname of the endpoint to which VDK logs will be sent through SysLog.",
        )
        config_builder.add(
            key=SYSLOG_PORT,
            default_value=514,
            description="The port of the endpoint to which VDK logs will be sent through SysLog.",
        )
        config_builder.add(
            key=SYSLOG_ENABLED,
            default_value=False,
            description="If set to True, SysLog log forwarding is enabled.",
        )
        config_builder.add(
            key=SYSLOG_SOCK_TYPE,
            default_value="UDP",
            description=f"Socket type for SysLog log forwarding connection. Currently possible values are {list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
        )

    @hookimpl
    def initialize_job(self, context: JobContext) -> None:
        """
        Initialize logging for running Data Job.

        When running a data job logging is more verbose, it includes more details like op id, job name.
        """

        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        job_name = context.name
        log_config_type = context.core_context.configuration.get_value(
            vdk_config.LOG_CONFIG
        )
        vdk_log_level = context.core_context.configuration.get_value(
            vdk_config.LOG_LEVEL_VDK
        )
        log_level_module = context.core_context.configuration.get_value(
            vdk_config.LOG_LEVEL_MODULE
        )
        syslog_url = context.core_context.configuration.get_value(SYSLOG_URL)
        syslog_port = context.core_context.configuration.get_value(SYSLOG_PORT)
        syslog_sock_type = context.core_context.configuration.get_value(
            SYSLOG_SOCK_TYPE
        )
        syslog_enabled = context.core_context.configuration.get_value(SYSLOG_ENABLED)
        try:  # If logging initialization fails we want to attempt sending telemetry before exiting VDK
            if not os.environ.get("VDK_USE_STRUCTLOG"):
                configure_loggers(
                    job_name,
                    attempt_id,
                    log_config_type=log_config_type,
                    vdk_logging_level=vdk_log_level,
                    log_level_module=log_level_module,
                    syslog_args=(
                        syslog_url,
                        syslog_port,
                        syslog_sock_type,
                        syslog_enabled,
                    ),
                )
                log = logging.getLogger(__name__)
                log.debug(f"Initialized logging for log type {log_config_type}.")
            else:
                log = logging.getLogger(__name__)
                log.debug(
                    "VDK_USE_STRUCTLOG environment variable is set, so the logging config will rely on the "
                    "vdk-structlog plugin."
                )
        except Exception as e:
            # Have local logs on DEBUG level, when standard log configuration fails
            logging.basicConfig(level=logging.DEBUG)
            log = logging.getLogger(__name__)
            log.warning(
                "Logging configuration %s failed.\n"
                "Trying to send telemetry for Job attempt: %s"
                % (log_config_type, attempt_id)
            )
            errors.log_exception(
                logging.getLogger(__name__),
                e,
                "Failed to initialize logging",
                errors.MSG_WHY_FROM_EXCEPTION(e),
                "Failed to initialize data job logging."
                " Will proceed with basic local logging on"
                " DEBUG level.",
                "Depending on stacktrace.",
            )
