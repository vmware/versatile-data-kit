# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging.handlers

from vdk.plugin.structlog.constants import SYSLOG_PROTOCOLS
from vdk.plugin.structlog.filters import AttributeAdder


DETAILED_FORMAT = (
    "%(asctime)s [VDK] %(job_name)s [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
    "lineno)-4.4s %(funcName)-16.16s[id:%(attempt_id)s]- %(message)s"
)


def configure_syslog_handler(
    syslog_enabled,
    syslog_host,
    syslog_port,
    syslog_protocol,
    job_name="",
    attempt_id="no-id",
):
    # if not syslog_enabled:
    #     return None

    # if syslog_protocol not in SYSLOG_PROTOCOLS:
    #     raise ValueError(
    #         f"Provided configuration variable for SYSLOG_PROTOCOL has an invalid value. "
    #         f"VDK was run with SYSLOG_PROTOCOL={syslog_protocol}, however, "
    #         f"{syslog_protocol} is an invalid value for this variable. "
    #         f"Provide a valid value for SYSLOG_PROTOCOL. "
    #         f"Currently possible values are {list(SYSLOG_PROTOCOLS.keys())}"
    #     )

    # syslog_socktype = SYSLOG_PROTOCOLS[syslog_protocol.upper()]
    # syslog_handler = logging.handlers.SysLogHandler(
    #     address=(syslog_host, syslog_port),
    #     facility=logging.handlers.SysLogHandler.LOG_USER,
    #     socktype=syslog_socktype,
    # )

    # formatter = logging.Formatter(DETAILED_FORMAT)
    # syslog_handler.setFormatter(formatter)

    # job_name_adder = AttributeAdder("job_name", job_name)
    # attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

    # syslog_handler.addFilter(job_name_adder)
    # syslog_handler.addFilter(attempt_id_adder)

    # syslog_handler.setLevel("DEBUG")

    # return syslog_handler
    handler = logging.handlers.SysLogHandler(
        facility=logging.handlers.SysLogHandler.LOG_DAEMON, address="/dev/log"
    )
    formatter = logging.Formatter(DETAILED_FORMAT)
    handler.setFormatter(formatter)
    return handler
