# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import sys
from typing import List
from typing import Optional

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
from vdk.plugin.structlog.constants import parse_log_level_module
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_ALL_KEYS
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_KEY
from vdk.plugin.structlog.constants import SYSLOG_ENABLED
from vdk.plugin.structlog.constants import SYSLOG_PORT
from vdk.plugin.structlog.constants import SYSLOG_SOCK_TYPE
from vdk.plugin.structlog.constants import SYSLOG_SOCK_TYPE_VALUES_DICT
from vdk.plugin.structlog.constants import SYSLOG_URL
from vdk.plugin.structlog.filters import AttributeAdder
from vdk.plugin.structlog.formatters import create_formatter


def _set_already_configured() -> None:
    setattr(sys.modules[__name__], "logging_already_configured", True)


def _is_already_configured() -> bool:
    res = hasattr(sys.modules[__name__], "logging_already_configured")
    return res


def configure_loggers(
    job_name: str = "",
    attempt_id: str = "no-id",
    log_config_type: str = None,
    vdk_logging_level: str = "DEBUG",
    log_level_module: str = None,
    syslog_args: (str, int, str, bool) = ("localhost", 514, "UDP", False),
) -> None:
    """
    Configure logging for VDK and the user code.
    :param job_name: The name of the job.
    :param attempt_id: The id of the attempt.
    :param log_config_type: The type of the logging configuration.
    :param vdk_logging_level: The logging level for VDK.
    :param log_level_module: The logging level for the user code.
    :param syslog_args: The syslog arguments.
    """

    import logging.config

    if _is_already_configured():
        log = logging.getLogger(__name__)
        msg = "Logging already configured. This seems like a bug. Fix me!."
        # Plugins would override logging directly with logging library not through this method
        # it is probably OK for tests to configure logging twice. VDK, however, shouldn't.
        log.warning(msg)

    # Likely most logging system (like Log Insight) show the hostname from where the syslog message arrived so no
    # need to include it here.
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
    _LOGGERS.update(parse_log_level_module(log_level_module))

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
                f"VDK was run with {SYSLOG_SOCK_TYPE}={syslog_sock_type}, however {syslog_sock_type} is invalid value "
                f"for this variable. Provide a valid value for {SYSLOG_SOCK_TYPE}."
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


"""
Handlers
https://docs.python.org/3/library/logging.html#handler-objects
https://docs.python.org/3/howto/logging-cookbook.html#imparting-contextual-information-in-handlers

Filters
https://docs.python.org/3/library/logging.html#filter-objects

LogRecords
https://docs.python.org/3/library/logging.html#logrecord-objects

Additional reading

https://docs.python.org/3/howto/logging.html
https://realpython.com/python-logging/
https://realpython.com/python-logging-source-code/

Logging adapters a.k.a. bound loggers
https://docs.python.org/3/howto/logging-cookbook.html#context-info

Example:

class BoundLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # merge bound extra dict with existing extra dict if any
        if "extra" in kwargs:
            kwargs["extra"] = {**self.extra, **kwargs["extra"]}
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs


log = logging.getLogger(__name__)
bound = BoundLogger(log, {"bound_key": "bound_value"})
bound.warning("From vdk_initialize", extra={"first": "first_value", "second": "second_value"})
bound.warning("Something else from vdk_initialize")

"""


class StructlogPlugin:
    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        config_builder.add(
            key=STRUCTLOG_LOGGING_METADATA_KEY,
            default_value=",".join(
                list(JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT.keys())
            ),
            description=(
                f"Possible values: {STRUCTLOG_LOGGING_METADATA_ALL_KEYS}"
                "User-defined key-value pairs added to the logger's context will be displayed after the metadata, "
                "but before the message"
                "Keys for user-defined key-value pairs have to be added in this config option for the values to be "
                "displayed in the metadata"
            ),
        )

        config_builder.add(
            key=STRUCTLOG_LOGGING_FORMAT_KEY,
            default_value=STRUCTLOG_LOGGING_FORMAT_DEFAULT,
            description=(
                f"Controls the logging output format. Possible values: {STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES}"
            ),
        )

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
            description=f"Socket type for SysLog log forwarding connection. Currently possible values are "
            f"{list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
        )

    @hookimpl
    def vdk_initialize(self, context: CoreContext):
        os.environ["VDK_USE_STRUCTLOG"] = "1"
        metadata_keys = context.configuration.get_value(STRUCTLOG_LOGGING_METADATA_KEY)
        logging_formatter = context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)

        root_logger = logging.getLogger()
        log_level = (
            context.configuration.get_value(vdk_config.LOG_LEVEL_VDK)
            or os.environ.get("LOG_LEVEL_VDK")
            or os.environ.get("VDK_LOG_LEVEL_VDK")
        )
        if log_level:
            root_logger.setLevel(log_level.upper())
        else:
            if root_logger.getEffectiveLevel() == logging.NOTSET:
                root_logger.setLevel("WARNING")

        handler = logging.StreamHandler(sys.stderr)
        handler.addFilter(metadata_filter)
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)

    @hookimpl(hookwrapper=True)
    def initialize_job(self, context: JobContext) -> None:
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

        syslog_args = (
            context.core_context.configuration.get_value(SYSLOG_URL),
            context.core_context.configuration.get_value(SYSLOG_PORT),
            context.core_context.configuration.get_value(SYSLOG_SOCK_TYPE),
            context.core_context.configuration.get_value(SYSLOG_ENABLED),
        )
        configure_loggers(
            job_name,
            attempt_id,
            log_config_type,
            vdk_log_level,
            log_level_module,
            syslog_args,
        )
        parse_log_level_module(log_level_module)
        logging_formatter = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        metadata_keys = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_METADATA_KEY
        )

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)
        job_name_adder = AttributeAdder("vdk_job_name", job_name)

        root_logger = logging.getLogger()

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler.addFilter(job_name_adder)
        handler.addFilter(metadata_filter)

        root_logger.addHandler(handler)

        out: HookCallResult
        out = yield

        root_logger.removeHandler(handler)

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        logging_formatter = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        metadata_keys = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_METADATA_KEY
        )

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)
        job_name_adder = AttributeAdder("vdk_job_name", context.name)

        root_logger = logging.getLogger()
        if root_logger.handlers:
            root_logger.removeHandler(root_logger.handlers[0])

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler.addFilter(job_name_adder)
        handler.addFilter(metadata_filter)

        root_logger.addHandler(handler)

        out: HookCallResult
        out = yield

        # do not remove the handler, we need it until the end

    @hookimpl(hookwrapper=True)
    def run_step(self, context: JobContext, step: Step) -> Optional[StepResult]:
        root_logger = logging.getLogger()
        step_name_adder = AttributeAdder("vdk_step_name", step.name)
        step_type_adder = AttributeAdder("vdk_step_type", step.type)
        for handler in root_logger.handlers:
            handler.addFilter(step_name_adder)
            handler.addFilter(step_type_adder)
        out: HookCallResult
        out = yield
        for handler in root_logger.handlers:
            handler.removeFilter(step_name_adder)
            handler.removeFilter(step_type_adder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(StructlogPlugin(), "StructlogPlugin")
