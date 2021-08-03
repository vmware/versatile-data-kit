# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import types
from sys import modules
from typing import cast

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config import vdk_config
from taurus.vdk.builtin_plugins.run.job_context import JobContext
from taurus.vdk.core import errors
from taurus.vdk.core.statestore import CommonStoreKeys


def configure_loggers(
    job_name: str = "",
    attempt_id: str = "no-id",
    log_config_type: str = None,
    vdk_logging_level: str = "DEBUG",
) -> None:
    """
    Configure default logging configuration

    :param job_name: the name of the job
    :param attempt_id: the id of the current job run attempt
    :param log_config_type: where the job is executed: CLOUD or LOCAL
    :param vdk_logging_level: The level for vdk specific logs.
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
        "%(asctime)s=%(created)10.0f[VDK] {} [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
        "lineno)-4.4s %(funcName)-16.16s[OpId:{}]- %(message)s".format(
            job_name, attempt_id
        )
    )

    _LOGGERS = {
        "requests_kerberos": {"level": "INFO"},
        "requests_oauthlib": {"level": "INFO"},
        "urllib3": {"level": "INFO"},
        "taurus": {"level": vdk_logging_level},
    }

    _FORMATTERS = {"detailedFormatter": {"format": DETAILED_FORMAT}}

    _CONSOLE_HANDLER = {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "detailedFormatter",
        "stream": "ext://sys.stderr",
    }

    if "CLOUD" == log_config_type:
        CLOUD = {  # @UnusedVariable
            "version": 1,
            "handlers": {"consoleHandler": _CONSOLE_HANDLER},
            "formatters": _FORMATTERS,
            "root": {"handlers": ["consoleHandler"], "level": "INFO"},
            "loggers": _LOGGERS,
            "disable_existing_loggers": False,
        }
        logging.config.dictConfig(CLOUD)
    elif "NONE" == log_config_type:
        pass
    else:
        LOCAL = {  # @UnusedVariable
            "version": 1,
            "handlers": {"consoleHandler": _CONSOLE_HANDLER},
            "formatters": _FORMATTERS,
            "root": {"handlers": ("consoleHandler",), "level": "DEBUG"},
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
        try:  # If logging initialization fails we want to attempt sending telemetry before exiting VDK
            configure_loggers(
                job_name,
                attempt_id,
                log_config_type=log_config_type,
                vdk_logging_level=vdk_log_level,
            )
            log = logging.getLogger(__name__)
            log.debug(f"Initialized logging for log type {log_config_type}.")
        except Exception as e:
            # Have local logs on DEBUG level, when standard log configuration fails
            logging.basicConfig(level=logging.DEBUG)
            log = logging.getLogger(__name__)
            log.warning(
                "Logging configuration %s failed.\n"
                "Trying to send telemetry for Job attempt: %s"
                % (log_config_type, attempt_id)
            )
            errors.log_and_rethrow(
                errors.find_whom_to_blame_from_exception(e),
                log=logging.getLogger(__name__),
                what_happened="Failed to initialize logging",
                why_it_happened=errors.MSG_WHY_FROM_EXCEPTION(e),
                consequences="Logging is critical VDK component. VDK will now exit.",
                countermeasures="Depending on stacktrace",
                exception=e,
            )
