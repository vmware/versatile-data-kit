import logging.handlers

from vdk.internal.builtin_plugins.run.job_context import JobContext

from vdk.plugin.structlog.constants import SYSLOG_PROTOCOLS, SYSLOG_ENABLED_KEY, SYSLOG_HOST_KEY, SYSLOG_PORT_KEY, \
    SYSLOG_PROTOCOL_KEY


class JobContextFilter(logging.Filter):
    """
    A custom logging filter that adds job-specific context to log records.

    This filter injects 'job_name' and 'attempt_id' attributes into each log record,
    allowing these details to be included in the log messages formatted by log handlers.

    The filter can be added to any standard Python logger. Once added, all log messages
    emitted by this logger will include the 'job_name' and 'attempt_id' information.
    """
    def __init__(self, job_name, attempt_id):
        super().__init__()
        self.job_name = job_name
        self.attempt_id = attempt_id

    def filter(self, record):
        record.job_name = self.job_name
        record.attempt_id = self.attempt_id
        return True


DETAILED_FORMAT = (
    "%(asctime)s [VDK] %(job_name)s [%(levelname)-5.5s] %(name)-30.30s %(filename)20.20s:%("
    "lineno)-4.4s %(funcName)-16.16s[id:%(attempt_id)s]- %(message)s"
)


def configure_syslog_handler(context: JobContext, job_name="", attempt_id="no-id"):
    syslog_enabled = context.core_context.configuration.get_value(SYSLOG_ENABLED_KEY)
    if not syslog_enabled:
        return None

    syslog_host = context.core_context.configuration.get_value(SYSLOG_HOST_KEY)
    syslog_port = context.core_context.configuration.get_value(SYSLOG_PORT_KEY)
    syslog_protocol = context.core_context.configuration.get_value(SYSLOG_PROTOCOL_KEY)

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
        facility=logging.handlers.SysLogHandler.LOG_USER,
        socktype=syslog_socktype
    )

    context_filter = JobContextFilter(job_name, attempt_id)
    syslog_handler.addFilter(context_filter)

    formatter = logging.Formatter(DETAILED_FORMAT)
    syslog_handler.setFormatter(formatter)

    syslog_handler.setLevel("DEBUG")

    return syslog_handler
