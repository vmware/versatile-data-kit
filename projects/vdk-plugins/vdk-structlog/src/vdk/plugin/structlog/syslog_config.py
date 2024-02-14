# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging.handlers

from vdk.plugin.structlog.constants import SYSLOG_PROTOCOLS


def create_syslog_handler(
    syslog_enabled,
    syslog_host,
    syslog_port,
    syslog_protocol,
):
    if not syslog_enabled:
        return None

    if syslog_protocol not in SYSLOG_PROTOCOLS:
        raise ValueError(
            f"Provided configuration variable for SYSLOG_PROTOCOL has an invalid value. "
            f"VDK was run with SYSLOG_PROTOCOL={syslog_protocol}, however, "
            f"{syslog_protocol} is an invalid value for this variable. "
            f"Provide a valid value for SYSLOG_PROTOCOL. "
            f"Currently possible values are {list(SYSLOG_PROTOCOLS.keys())}"
        )

    syslog_socktype = SYSLOG_PROTOCOLS[syslog_protocol.upper()]
    syslog_handler = logging.handlers.SysLogHandler(
        address=(syslog_host, syslog_port),
        facility=logging.handlers.SysLogHandler.LOG_DAEMON,
        socktype=syslog_socktype,
    )

    syslog_handler.setLevel("DEBUG")

    return syslog_handler
