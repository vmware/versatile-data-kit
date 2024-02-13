# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.builtin_plugins.config import vdk_config
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_ENABLED
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_HOST
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PORT
from vdk.plugin.structlog.constants import DEFAULT_SYSLOG_PROTOCOL
from vdk.plugin.structlog.constants import DETAILED_LOGGING_FORMAT
from vdk.plugin.structlog.constants import JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT
from vdk.plugin.structlog.constants import STRUCTLOG_CONFIG_PRESET
from vdk.plugin.structlog.constants import STRUCTLOG_CONSOLE_LOG_PATTERN
from vdk.plugin.structlog.constants import STRUCTLOG_FORMAT_INIT_LOGS
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
                STRUCTLOG_FORMAT_INIT_LOGS: False,
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
                STRUCTLOG_FORMAT_INIT_LOGS: True,
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

    def get_format_init_logs(self) -> str:
        return self._config[STRUCTLOG_FORMAT_INIT_LOGS]


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=STRUCTLOG_LOGGING_METADATA_KEY,
        default_value=",".join(list(JSON_STRUCTLOG_LOGGING_METADATA_DEFAULT.keys())),
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

    config_builder.add(
        key=STRUCTLOG_FORMAT_INIT_LOGS,
        default_value=False,
        description="Set to True to apply structlog formatting options to the vdk initialization logs",
    )
