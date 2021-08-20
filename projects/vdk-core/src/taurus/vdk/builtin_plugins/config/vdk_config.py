# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import pathlib
from os import getenv
from typing import Optional

from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config.job_config import JobConfig
from taurus.vdk.builtin_plugins.config.job_config import JobConfigKeys
from taurus.vdk.core.config import ConfigurationBuilder

VDK_ = "VDK_"

# configuration keys:
DB_DEFAULT_TYPE = "DB_DEFAULT_TYPE"
JOB_GITHASH = "JOB_GITHASH"
LOG_CONFIG = "LOG_CONFIG"
LOG_LEVEL_VDK = "LOG_LEVEL_VDK"
WORKING_DIR = "WORKING_DIR"
EXECUTION_ID = "EXECUTION_ID"
OP_ID = "OP_ID"

log = logging.getLogger(__name__)


class CoreConfigDefinitionPlugin:
    """
    Define the core configuration.

    The configuration defaults to behavior needed by data engineers/analysts
       (i.e. running locally against production with no monitoring and console logging)
    Automated execution in cloud should override:
       1. VDK_MONITORING_ENABLED = True
       2. VDK_LOG_CONFIG = CLOUD
       4. VDK_WORKING_DIR
    """

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        """Set common configuration necessary for vdk

        We are setting it as tryfirst to make sure any config provider afterwards would see the definitions.
        """

        # TODO: Get currently supported db types
        db_default_type_description = (
            "Default DB connection provided by VDK when executing a data job. "
            "All sql queries, templates/load that interacts with the Data Warehouse would be against that database."
            "Different database types can be configured with plugins. "
            "Current supported database types: TODO \n"
        )
        config_builder.add(DB_DEFAULT_TYPE, None, True, db_default_type_description)

        config_builder.add(
            WORKING_DIR, "."
        )  # Use '.' when running on the cloud. User ssh-admin has rights to current folder

        config_builder.add("MONITORING_ENABLED", False)
        config_builder.add(
            LOG_CONFIG, "LOCAL"
        )  # {LOCAL, CLOUD, NONE} To be overridden when executing in cloud
        config_builder.add(
            LOG_LEVEL_VDK,
            "DEBUG",
            "Logging verbosity of VDK code can be controlled from here. "
            "Allowed values: CRITICAL, ERROR, WARNING, INFO, DEBUG",
        )
        config_builder.add(JOB_GITHASH, "unknown")
        config_builder.add(
            OP_ID,
            "",
            True,
            "An identifier to be associated with the current VDK run, "
            "or an empty string, to auto generate the identifier.",
        )
        config_builder.add(
            EXECUTION_ID,
            "",
            True,
            "An identifier to be associated with the current VDK run, "
            "or an empty string, to auto generate the identifier.",
        )


class EnvironmentVarsConfigPlugin:
    """
    Configuration loaded from environment variables.
    """

    @hookimpl(trylast=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        """
        Infer config values from environment variables.
        """
        log.info(
            "Will try to detect configuration from environment variables (using VDK_{KEY_NAME})"
        )
        description = """Attempts to load all defined configurations using environment variables by adding prefix "VDK_".
For example: if config with key "my_key" is defined, it will search for environment variables "VDK_MY_KEY"
If a key is defined with a dot it will be replaced with underscore - 'my.key' it will lookup env variable "VDK_MY_KEY"
Note: Configuration that you set with environment variables affects only local development..
Configuration for cloud execution is done in 'config.ini' file or the vdk cli.
         """
        config_builder.add(
            key="__config_provider__ environment variables",
            default_value="always_enabled",
            description=description,
        )

        config_keys = config_builder.list_config_keys()
        log.debug(
            f"Founds config keys: {config_keys}. Will check if environment variable is set for any"
        )
        for key in config_keys:
            value = getenv(VDK_ + key.replace(".", "_").upper())
            if value is not None:
                log.debug(f"Found environment variable for key {key}")
                config_builder.set_value(key, value)


class JobConfigIniPlugin:
    def __init__(self):
        self.__job_path: Optional[pathlib.Path] = None

    @hookimpl
    def vdk_start(self, command_line_args: list) -> None:
        # TODO: improve hooks/plugin framework to enable per sub-command configuration in a less hacky way.
        if command_line_args and "run" in command_line_args:
            index = command_line_args.index("run")
            if len(command_line_args) > index + 1:
                self.__job_path = pathlib.Path(command_line_args[index + 1])

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        description = f"""Used only during vdk run only - load configuration specified in
config.ini file in the data job's root directory. It can be overridden by environment variables configuration.
config.ini loads only specific configuration and is used for legacy reasons.
The following options are set with config.ini: {[e.value for e in JobConfigKeys]}
         """
        if (
            self.__job_path
            and self.__job_path.exists()
            and self.__job_path.is_dir()
            and self.__job_path.joinpath("config.ini").exists()
        ):
            print("Detected config.ini. Will try to read config.ini.")
            config_builder.add(
                key="__config_provider__job config ini",
                default_value="always_enabled",
                description=description,
            )

            job_config = JobConfig(self.__job_path)
            config_builder.set_value(JobConfigKeys.TEAM, job_config.get_team())
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR,
                job_config.get_contacts_notified_on_job_failure_user_error(),
            )
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS,
                job_config.get_contacts_notified_on_job_success(),
            )
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR,
                job_config.get_contacts_notified_on_job_failure_platform_error(),
            )
            config_builder.set_value(
                JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS,
                job_config.get_enable_attempt_notifications(),
            )
