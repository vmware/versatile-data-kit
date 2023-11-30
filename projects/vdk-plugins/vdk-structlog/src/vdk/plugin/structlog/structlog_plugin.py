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
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core import errors
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
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
        # merge bound extra dict with existing exra dict if any
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
                "User-defined key-value pairs added to the logger's context will be displayed after the metadata, but before the message"
                "Keys for user-defined key-value pairs have to be added in this config option for the values to be displayed in the metadata"
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
        syslog_url = context.configuration.get_value(SYSLOG_URL)
        syslog_port = context.configuration.get_value(SYSLOG_PORT)
        syslog_sock_type = context.configuration.get_value(SYSLOG_SOCK_TYPE)
        syslog_enabled = context.configuration.get_value(SYSLOG_ENABLED)

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])

        handler = logging.StreamHandler(sys.stderr)
        handler.addFilter(metadata_filter)
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)

        if syslog_sock_type not in SYSLOG_SOCK_TYPE_VALUES_DICT:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"Provided configuration variable for {SYSLOG_SOCK_TYPE} has invalid value.",
                    f"VDK was run with {SYSLOG_SOCK_TYPE}={syslog_sock_type}, however {syslog_sock_type} is invalid "
                    f"value for this variable. Provide a valid value for {SYSLOG_SOCK_TYPE}."
                    f"Currently possible values are {list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
                )
            )

        if syslog_enabled:
            syslog_handler = logging.handlers.SysLogHandler(
                address=(
                    syslog_url,
                    syslog_port,
                ),
                socktype=SYSLOG_SOCK_TYPE_VALUES_DICT[syslog_sock_type],
                facility="user",
            )
            syslog_handler.setLevel(logging.DEBUG)
            syslog_handler.setFormatter(formatter)
            syslog_handler.addFilter(metadata_filter)
            root_logger.addHandler(syslog_handler)

    @hookimpl(hookwrapper=True)
    def initialize_job(self, context: JobContext) -> None:
        logging_formatter = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        metadata_keys = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_METADATA_KEY
        )
        syslog_url = context.core_context.configuration.get_value(SYSLOG_URL)
        syslog_port = context.core_context.configuration.get_value(SYSLOG_PORT)
        syslog_sock_type = context.core_context.configuration.get_value(
            SYSLOG_SOCK_TYPE
        )
        syslog_enabled = context.core_context.configuration.get_value(SYSLOG_ENABLED)

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)
        job_name_adder = AttributeAdder("vdk_job_name", context.name)

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler.addFilter(job_name_adder)
        handler.addFilter(metadata_filter)

        root_logger.addHandler(handler)

        if syslog_sock_type not in SYSLOG_SOCK_TYPE_VALUES_DICT:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"Provided configuration variable for {SYSLOG_SOCK_TYPE} has invalid value.",
                    f"VDK was run with {SYSLOG_SOCK_TYPE}={syslog_sock_type}, however {syslog_sock_type} is invalid "
                    f"value for this variable. Provide a valid value for {SYSLOG_SOCK_TYPE}."
                    f"Currently possible values are {list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
                )
            )

        if syslog_enabled:
            syslog_handler = logging.handlers.SysLogHandler(
                address=(
                    syslog_url,
                    syslog_port,
                ),
                socktype=SYSLOG_SOCK_TYPE_VALUES_DICT[syslog_sock_type],
                facility="user",
            )
            syslog_handler.setLevel(logging.DEBUG)
            syslog_handler.setFormatter(formatter)
            syslog_handler.addFilter(job_name_adder)
            syslog_handler.addFilter(metadata_filter)
            root_logger.addHandler(syslog_handler)

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
        syslog_url = context.core_context.configuration.get_value(SYSLOG_URL)
        syslog_port = context.core_context.configuration.get_value(SYSLOG_PORT)
        syslog_sock_type = context.core_context.configuration.get_value(
            SYSLOG_SOCK_TYPE
        )
        syslog_enabled = context.core_context.configuration.get_value(SYSLOG_ENABLED)

        formatter, metadata_filter = create_formatter(logging_formatter, metadata_keys)
        job_name_adder = AttributeAdder("vdk_job_name", context.name)

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])

        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler.addFilter(job_name_adder)
        handler.addFilter(metadata_filter)

        root_logger.addHandler(handler)

        if syslog_sock_type not in SYSLOG_SOCK_TYPE_VALUES_DICT:
            errors.report_and_throw(
                errors.VdkConfigurationError(
                    f"Provided configuration variable for {SYSLOG_SOCK_TYPE} has invalid value.",
                    f"VDK was run with {SYSLOG_SOCK_TYPE}={syslog_sock_type}, however {syslog_sock_type} is invalid "
                    f"value for this variable. Provide a valid value for {SYSLOG_SOCK_TYPE}."
                    f"Currently possible values are {list(SYSLOG_SOCK_TYPE_VALUES_DICT.keys())}",
                )
            )

        if syslog_enabled:
            syslog_handler = logging.handlers.SysLogHandler(
                address=(
                    syslog_url,
                    syslog_port,
                ),
                socktype=SYSLOG_SOCK_TYPE_VALUES_DICT[syslog_sock_type],
                facility="user",
            )
            syslog_handler.setLevel(logging.DEBUG)
            syslog_handler.setFormatter(formatter)
            syslog_handler.addFilter(job_name_adder)
            syslog_handler.addFilter(metadata_filter)
            root_logger.addHandler(syslog_handler)

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
