import logging.handlers

from vdk.internal.core.context import CoreContext

from vdk.plugin.structlog.constants import SYSLOG_PROTOCOLS, SYSLOG_ENABLED_KEY, SYSLOG_HOST_KEY, SYSLOG_PORT_KEY, \
    SYSLOG_PROTOCOL_KEY


def configure_syslog_handler(context: CoreContext):
    syslog_enabled = context.configuration.get_value(SYSLOG_ENABLED_KEY)
    if not syslog_enabled:
        return None

    syslog_host = context.configuration.get_value(SYSLOG_HOST_KEY)
    syslog_port = context.configuration.get_value(SYSLOG_PORT_KEY)
    syslog_protocol = context.configuration.get_value(SYSLOG_PROTOCOL_KEY)

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
        socktype=syslog_socktype
    )

    syslog_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    syslog_handler.setFormatter(formatter)

    return syslog_handler
