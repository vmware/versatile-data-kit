# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
from typing import List
from typing import Optional

from pythonjsonlogger import jsonlogger
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import HookCallResult
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.execution_results import StepResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.builtin_plugins.run.step import Step
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_CONSOLE_LOG_PATTERN
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_ALL_KEYS
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_KEY
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
            key=STRUCTLOG_CONSOLE_LOG_PATTERN,
            default_value="",
            description="Custom format string for console logging. Leave empty for default format.",
        )

        config_builder.add(
            key=STRUCTLOG_LOGGING_FORMAT_KEY,
            default_value=STRUCTLOG_LOGGING_FORMAT_DEFAULT,
            description=(
                f"Controls the logging output format. Possible values: {STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES}"
            ),
        )

    @hookimpl
    def vdk_initialize(self, context: CoreContext):
        metadata_keys = context.configuration.get_value(STRUCTLOG_LOGGING_METADATA_KEY)
        logging_formatter = context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        custom_format_string = context.configuration.get_value(
            STRUCTLOG_CONSOLE_LOG_PATTERN
        )

        formatter, metadata_filter = create_formatter(
            logging_formatter, metadata_keys, custom_format_string
        )

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])

        handler = logging.StreamHandler(sys.stderr)
        handler.addFilter(metadata_filter)
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)

    @hookimpl(hookwrapper=True)
    def initialize_job(self, context: JobContext) -> None:
        metadata_keys = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_METADATA_KEY
        )
        logging_formatter = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        custom_format_string = context.core_context.configuration.get_value(
            STRUCTLOG_CONSOLE_LOG_PATTERN
        )

        formatter, metadata_filter = create_formatter(
            logging_formatter, metadata_keys, custom_format_string
        )
        job_name_adder = AttributeAdder("vdk_job_name", context.name)

        root_logger = logging.getLogger()
        root_logger.removeHandler(root_logger.handlers[0])

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
        metadata_keys = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_METADATA_KEY
        )
        logging_formatter = context.core_context.configuration.get_value(
            STRUCTLOG_LOGGING_FORMAT_KEY
        )
        custom_format_string = context.core_context.configuration.get_value(
            STRUCTLOG_CONSOLE_LOG_PATTERN
        )

        formatter, metadata_filter = create_formatter(
            logging_formatter, metadata_keys, custom_format_string
        )
        job_name_adder = AttributeAdder("vdk_job_name", context.name)

        root_logger = logging.getLogger()
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
        handler = root_logger.handlers[0]

        # make sure the metadata filter executes last
        # so that step_name and step_type are filtered if necessary
        metadata_filter = [f for f in handler.filters if f.name == "metadata_filter"][0]
        handler.removeFilter(metadata_filter)

        step_name_adder = AttributeAdder("vdk_step_name", step.name)
        step_type_adder = AttributeAdder("vdk_step_type", step.type)
        handler.addFilter(step_name_adder)
        handler.addFilter(step_type_adder)

        # make sure the metadata filter executes last
        # so that step_name and step_type are filtered if necessary
        handler.addFilter(metadata_filter)
        out: HookCallResult
        out = yield
        handler.removeFilter(step_name_adder)
        handler.removeFilter(step_type_adder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(StructlogPlugin(), "StructlogPlugin")
