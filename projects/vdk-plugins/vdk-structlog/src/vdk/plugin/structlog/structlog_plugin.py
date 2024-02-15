# Copyright 2021-2024 VMware, Inc.
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
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_ENABLED
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_HOST
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PORT
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PROTOCOL
from vdk.plugin.structlog.constants import DETAILED_LOGGING_FORMAT
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_CONFIG_PRESET
from vdk.plugin.structlog.constants import STRUCTLOG_CONSOLE_LOG_PATTERN
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_FORMAT_POSSIBLE_VALUES
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_ALL_KEYS
from vdk.plugin.structlog.constants import STRUCTLOG_LOGGING_METADATA_KEY
from vdk.plugin.structlog.constants import STRUCTLOG_USE_STRUCTLOG
from vdk.plugin.structlog.constants import SYSLOG_ENABLED_KEY
from vdk.plugin.structlog.constants import SYSLOG_HOST_KEY
from vdk.plugin.structlog.constants import SYSLOG_PORT_KEY
from vdk.plugin.structlog.constants import SYSLOG_PROTOCOL_KEY
from vdk.plugin.structlog.filters import AttributeAdder
from vdk.plugin.structlog.formatters import create_formatter
from vdk.plugin.structlog.log_level_utils import set_non_root_log_levels
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


class StructlogConfig:
    def __init__(self, configuration: Configuration):
        presets = {
            "LOCAL": {
                STRUCTLOG_USE_STRUCTLOG: configuration.get_value(
                    STRUCTLOG_USE_STRUCTLOG
                ),
                STRUCTLOG_LOGGING_METADATA_KEY: ",".join(
                    list(JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT.keys())
                ),
                STRUCTLOG_LOGGING_FORMAT_KEY: STRUCTLOG_LOGGING_FORMAT_DEFAULT,
                STRUCTLOG_CONSOLE_LOG_PATTERN: "",
                STRUCTLOG_CONFIG_PRESET: configuration.get_value(
                    STRUCTLOG_CONFIG_PRESET
                ),
                SYSLOG_HOST_KEY: DEFAULT_SYSLOG_HOST,
                SYSLOG_PORT_KEY: DEFAULT_SYSLOG_PORT,
                SYSLOG_PROTOCOL_KEY: DEFAULT_SYSLOG_PROTOCOL,
                SYSLOG_ENABLED_KEY: DEFAULT_SYSLOG_ENABLED,
                vdk_config.LOG_LEVEL_VDK.lower(): configuration.get_value(
                    vdk_config.LOG_LEVEL_VDK.lower()
                ),
                vdk_config.LOG_LEVEL_MODULE.lower(): configuration.get_value(
                    vdk_config.LOG_LEVEL_MODULE.lower()
                ),
            },
            "CLOUD": {
                STRUCTLOG_USE_STRUCTLOG: configuration.get_value(
                    STRUCTLOG_USE_STRUCTLOG
                ),
                STRUCTLOG_LOGGING_METADATA_KEY: "",
                STRUCTLOG_LOGGING_FORMAT_KEY: STRUCTLOG_LOGGING_FORMAT_DEFAULT,
                STRUCTLOG_CONSOLE_LOG_PATTERN: DETAILED_LOGGING_FORMAT,
                STRUCTLOG_CONFIG_PRESET: configuration.get_value(
                    STRUCTLOG_CONFIG_PRESET
                ),
                SYSLOG_HOST_KEY: DEFAULT_SYSLOG_HOST,
                SYSLOG_PORT_KEY: DEFAULT_SYSLOG_PORT,
                SYSLOG_PROTOCOL_KEY: DEFAULT_SYSLOG_PROTOCOL,
                SYSLOG_ENABLED_KEY: DEFAULT_SYSLOG_ENABLED,
                vdk_config.LOG_LEVEL_VDK.lower(): configuration.get_value(
                    vdk_config.LOG_LEVEL_VDK.lower()
                ),
                vdk_config.LOG_LEVEL_MODULE.lower(): configuration.get_value(
                    vdk_config.LOG_LEVEL_MODULE.lower()
                ),
            },
        }

        self._config = presets[configuration.get_value(STRUCTLOG_CONFIG_PRESET)]

        for key in configuration.list_config_keys():
            if not configuration.is_default(key):
                self._config[key] = configuration.get_value(key)

    def get_use_structlog(self) -> bool:
        return self._config[STRUCTLOG_USE_STRUCTLOG]

    def get_structlog_logging_metadata(self) -> str:
        return self._config[STRUCTLOG_LOGGING_METADATA_KEY]

    def get_structlog_logging_format(self) -> str:
        return self._config[STRUCTLOG_LOGGING_FORMAT_KEY]

    def get_structlog_console_log_pattern(self) -> str:
        return self._config[STRUCTLOG_CONSOLE_LOG_PATTERN]

    def get_structlog_config_preset(self) -> str:
        return self._config[STRUCTLOG_CONFIG_PRESET]

    def get_syslog_host(self) -> str:
        return self._config[SYSLOG_HOST_KEY]

    def get_syslog_port(self) -> int:
        return self._config[SYSLOG_PORT_KEY]

    def get_syslog_protocol(self) -> str:
        return self._config[SYSLOG_PROTOCOL_KEY]

    def get_syslog_enabled(self) -> bool:
        return self._config[SYSLOG_ENABLED_KEY]

    def get_log_level_vdk(self) -> str:
        return self._config[vdk_config.LOG_LEVEL_VDK.lower()]

    def get_log_level_module(self) -> str:
        return self._config[vdk_config.LOG_LEVEL_MODULE.lower()]


class StructlogPlugin:
    def __init__(self):
        self._config = None

    def _get_syslog_config(self, context: CoreContext):
        syslog_enabled = self._config.get_syslog_enabled()
        syslog_host = self._config.get_syslog_host()
        syslog_port = self._config.get_syslog_port()
        syslog_protocol = self._config.get_syslog_protocol()

        return syslog_enabled, syslog_host, syslog_port, syslog_protocol

    def _create_formatter_and_metadata_filter(self, context: CoreContext):
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

    def _configure_root_logger(self, context: CoreContext, formatter, *filters):
        self._clear_root_logger_handlers()
        root_logger = logging.getLogger()

        handlers = [logging.StreamHandler(sys.stderr)]

        syslog_config = self._get_syslog_config(context)
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

        config_builder.add(
            key=SYSLOG_HOST_KEY,
            default_value=DEFAULT_SYSLOG_HOST,
            description="Hostname of the Syslog server.",
        )

        config_builder.add(
            key=SYSLOG_PORT_KEY,
            default_value=DEFAULT_SYSLOG_PORT,
            description="Port of the Syslog server.",
        )

        config_builder.add(
            key=SYSLOG_PROTOCOL_KEY,
            default_value=DEFAULT_SYSLOG_PROTOCOL,
            description="Syslog protocol (UDP or TCP).",
        )

        config_builder.add(
            key=SYSLOG_ENABLED_KEY,
            default_value=DEFAULT_SYSLOG_ENABLED,
            description="Enable Syslog logging (True or False).",
        )

        config_builder.add(
            key=STRUCTLOG_CONFIG_PRESET,
            default_value="LOCAL",
            description="Choose configuration preset. Any config options set together with the preset will override "
            "the preset options. Available presets: LOCAL, CLOUD",
        )

        config_builder.add(
            key=STRUCTLOG_USE_STRUCTLOG,
            default_value=True,
            description="Use the structlog logging config instead of using the one in vdk-core",
        )

    @hookimpl
    def vdk_initialize(self, context: CoreContext):
        self._config = StructlogConfig(context.configuration)

        formatter, metadata_filter = self._create_formatter_and_metadata_filter(context)

        attempt_id = context.state.get(CommonStoreKeys.ATTEMPT_ID)
        attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

        # Add placeholder values in case of custom format string
        job_name_adder = AttributeAdder("vdk_job_name", "")
        step_name_adder = AttributeAdder("vdk_step_name", "")
        step_type_adder = AttributeAdder("vdk_step_type", "")

        self._configure_root_logger(
            context,
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
        formatter, metadata_filter = self._create_formatter_and_metadata_filter(
            context.core_context
        )

        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

        job_name = context.name
        job_name_adder = AttributeAdder("vdk_job_name", job_name)

        # Add placeholder values in case of custom format string
        step_name_adder = AttributeAdder("vdk_step_name", "")
        step_type_adder = AttributeAdder("vdk_step_type", "")

        self._configure_root_logger(
            context.core_context,
            formatter,
            attempt_id_adder,
            job_name_adder,
            step_name_adder,
            step_type_adder,
            metadata_filter,
        )
        self._configure_non_root_log_levels()
        out: HookCallResult
        out = yield

        self._clear_root_logger_handlers()

    @hookimpl(hookwrapper=True)
    def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
        formatter, metadata_filter = self._create_formatter_and_metadata_filter(
            context.core_context
        )

        attempt_id = context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
        attempt_id_adder = AttributeAdder("attempt_id", attempt_id)

        job_name = context.name
        job_name_adder = AttributeAdder("vdk_job_name", job_name)

        # Add placeholder values in case of custom format string
        step_name_adder = AttributeAdder("vdk_step_name", "")
        step_type_adder = AttributeAdder("vdk_step_type", "")

        self._configure_root_logger(
            context.core_context,
            formatter,
            attempt_id_adder,
            job_name_adder,
            step_name_adder,
            step_type_adder,
            metadata_filter,
        )
        self._configure_non_root_log_levels()

        out: HookCallResult
        out = yield
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
        out: HookCallResult
        out = yield
        for handler in root_logger.handlers:
            handler.removeFilter(step_name_adder)
            handler.removeFilter(step_type_adder)


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(StructlogPlugin(), "StructlogPlugin")
