# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
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
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.structlog.filters import AttributeAdder
from vdk.plugin.structlog.formatters import create_formatter
from vdk.plugin.structlog.log_level_utils import set_non_root_log_levels
from vdk.plugin.structlog.structlog_config import add_definitions
from vdk.plugin.structlog.structlog_config import StructlogConfig
from vdk.plugin.structlog.syslog_config import create_syslog_handler

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
    def __init__(self):
        self._config = None

    def _get_syslog_config(self):
        syslog_enabled = self._config.get_syslog_enabled()
        syslog_host = self._config.get_syslog_host()
        syslog_port = self._config.get_syslog_port()
        syslog_protocol = self._config.get_syslog_protocol()

        return syslog_enabled, syslog_host, syslog_port, syslog_protocol

    def _create_formatter_and_metadata_filter(self):
        metadata_keys = self._config.get_structlog_logging_metadata()
        logging_formatter = self._config.get_structlog_logging_format()
        custom_format_string = self._config.get_structlog_console_log_pattern()
        formatter, metadata_filter = create_formatter(
            logging_formatter, metadata_keys, custom_format_string
        )
        return formatter, metadata_filter

    def _configure_non_root_log_levels(self):
        vdk_log_level = self._config.get_log_level_vdk()
        if vdk_log_level is None:
            vdk_log_level = logging.getLogger().getEffectiveLevel()
        log_level_module = self._config.get_log_level_module()
        set_non_root_log_levels(vdk_log_level, log_level_module)

    def _clear_root_logger_handlers(self):
        root_logger = logging.getLogger()
        handlers_to_remove = root_logger.handlers
        for handler in handlers_to_remove:
            root_logger.removeHandler(handler)

    def _configure_root_logger(self, formatter, *filters):
        self._clear_root_logger_handlers()
        root_logger = logging.getLogger()

        handlers = [logging.StreamHandler(sys.stderr)]

        syslog_config = self._get_syslog_config()
        syslog_handler = create_syslog_handler(*syslog_config)
        if syslog_handler:
            handlers.append(syslog_handler)

        for handler in handlers:
            for f in filters:
                handler.addFilter(f)
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        add_definitions(config_builder)

    @hookimpl(tryfirst=True)
    def vdk_initialize(self, context: CoreContext):
        self._config = StructlogConfig(context.configuration)
        if self._config.get_format_init_logs():
            formatter, metadata_filter = self._create_formatter_and_metadata_filter()

            attempt_id = context.state.get(CommonStoreKeys.ATTEMPT_ID)
            attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

            # Add placeholder values in case of custom format string
            job_name_adder = AttributeAdder("vdk_job_name", "")
            step_name_adder = AttributeAdder("vdk_step_name", "")
            step_type_adder = AttributeAdder("vdk_step_type", "")

            self._configure_root_logger(
                formatter,
                attempt_id_adder,
                job_name_adder,
                step_name_adder,
                step_type_adder,
                metadata_filter,
            )
            self._configure_non_root_log_levels()

    @hookimpl(hookwrapper=True)
    def initialize_job(self, context: JobContext) -> None:
        formatter, metadata_filter = self._create_formatter_and_metadata_filter()

        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

        job_name = context.name
        job_name_adder = AttributeAdder("vdk_job_name", job_name)

        # Add placeholder values in case of custom format string
        step_name_adder = AttributeAdder("vdk_step_name", "")
        step_type_adder = AttributeAdder("vdk_step_type", "")

        self._configure_root_logger(
            formatter,
            attempt_id_adder,
            job_name_adder,
            step_name_adder,
            step_type_adder,
            metadata_filter,
        )
        self._configure_non_root_log_levels()
        yield

        self._clear_root_logger_handlers()

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        formatter, metadata_filter = self._create_formatter_and_metadata_filter()

        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

        job_name = context.name
        job_name_adder = AttributeAdder("vdk_job_name", job_name)

        # Add placeholder values in case of custom format string
        step_name_adder = AttributeAdder("vdk_step_name", "")
        step_type_adder = AttributeAdder("vdk_step_type", "")

        self._configure_root_logger(
            formatter,
            attempt_id_adder,
            job_name_adder,
            step_name_adder,
            step_type_adder,
            metadata_filter,
        )
        self._configure_non_root_log_levels()

        yield
        # do not remove handlers, we need them until the end

    @hookimpl(hookwrapper=True)
    def run_step(self, context: JobContext, step: Step) -> Optional[StepResult]:
        root_logger = logging.getLogger()
        step_name_adder = AttributeAdder("vdk_step_name", step.name)
        step_type_adder = AttributeAdder("vdk_step_type", step.type)

        for handler in root_logger.handlers:
            metadata_filter = None
            # make sure the metadata filter executes last
            # so that step_name and step_type are filtered if necessary
            metadata_filter_result = [
                f for f in handler.filters if f.name == "metadata_filter"
            ]
            if metadata_filter_result:
                metadata_filter = metadata_filter_result[0]

            if metadata_filter:
                handler.removeFilter(metadata_filter)

            handler.addFilter(step_name_adder)
            handler.addFilter(step_type_adder)

            # make sure the metadata filter executes last
            # so that step_name and step_type are filtered if necessary
            if metadata_filter:
                handler.addFilter(metadata_filter)
        yield
        for handler in root_logger.handlers:
            handler.removeFilter(step_name_adder)
            handler.removeFilter(step_type_adder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(StructlogPlugin(), "StructlogPlugin")
