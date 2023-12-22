import logging.handlers

from vdk.plugin.structlog.constants import SYSLOG_PROTOCOLS


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


def configure_syslog_handler(syslog_enabled, syslog_host, syslog_port, syslog_protocol, job_name="", attempt_id="no-id"):
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
        facility=logging.handlers.SysLogHandler.LOG_USER,
        socktype=syslog_socktype
    )

    context_filter = JobContextFilter(job_name, attempt_id)
    syslog_handler.addFilter(context_filter)

    formatter = logging.Formatter(DETAILED_FORMAT)
    syslog_handler.setFormatter(formatter)

    syslog_handler.setLevel("DEBUG")

    return syslog_handler
