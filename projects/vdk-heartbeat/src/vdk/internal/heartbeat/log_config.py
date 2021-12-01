# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import time
from sys import modules

from vdk.internal.heartbeat.config import Config


def configure_loggers(
    app_name="vdk-heartbeat",
    op_id=Config.DEFAULT_OP_ID,
    log_config_type=None,
    vdk_logging_level="INFO",
):
    """
    Configure logging for the current project

    :param op_id: Op ID generated during single execution of the tool
    :param log_config_type: NONE (logging disabled) or LOCAL  (print to console), by default it is local
    :param vdk_logging_level: same as logging module. By default it's DEBUG
    """
    import logging.config

    # Note Log Insight shows the hostname from where the syslog message arrived so no need to include it here.
    DETAILED_FORMAT = (
        f"%(asctime)s10.0 [%(levelname)-5.5s] [{app_name}] %(name)-10.10s "
        f"%(filename)10.10s:%(lineno)-4.4s %(funcName)-16.16s[OpId:{op_id}]- %(message)s"
    )

    _LOGGERS = {
        "taurus": {"level": vdk_logging_level},
    }

    _FORMATTERS = {
        "detailedFormatter": {
            "format": DETAILED_FORMAT,
        },
    }

    _CONSOLE_HANDLER = {
        "class": "logging.StreamHandler",
        "level": vdk_logging_level,
        "formatter": "detailedFormatter",
        "stream": "ext://sys.stderr",
    }

    if "NONE" == log_config_type:
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


def set_already_configured():
    setattr(modules[__name__], "logging_already_configured", True)


def is_already_configured():
    res = hasattr(modules[__name__], "logging_already_configured")
    return res
