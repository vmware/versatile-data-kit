# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from os import getenv
from typing import Optional

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.job_config import JobConfig
from vdk.internal.builtin_plugins.config.job_config import JobConfigKeys
from vdk.internal.core.config import ConfigurationBuilder

VDK_ = "VDK_"

# configuration keys:
DB_DEFAULT_TYPE = "DB_DEFAULT_TYPE"
JOB_GITHASH = "JOB_GITHASH"
LOG_CONFIG = "LOG_CONFIG"
LOG_LEVEL_VDK = "LOG_LEVEL_VDK"
WORKING_DIR = "WORKING_DIR"
ATTEMPT_ID = "ATTEMPT_ID"
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
            "All sql queries, templates/loads would be against that database."
            "Different database types can be configured with plugins. \n"
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
            None,
            True,
            "Logging verbosity of VDK code can be controlled from here. "
            "Allowed values: CRITICAL, ERROR, WARNING, INFO, DEBUG. "
            "If not set python default or one set by vdk -v LEVEL is used. ",
        )
        config_builder.add(JOB_GITHASH, "unknown")
        config_builder.add(
            OP_ID,
            "",
            True,
            "It identifies the trigger that initiated this job. "
            "If left empty it will be auto-generated."
            "OP ID is similar to trace ID in open tracing."
            "It enable tracing multiple operations across difference services and datasets"
            "For example, it is possible to have N jobs with same OpID (if Job1 started Job2 then Job1.opId = "
            "Job2.opId). "
            "In HTTP requests it is passed as header 'X-OPID' by the Control Service.",
        )
        config_builder.add(
            EXECUTION_ID,
            "",
            True,
            "An identifier to be associated with the current VDK execution."
            "If left empty it will be auto-generated. "
            "An instance of a running Data Job deployment is called an execution. "
            "Data Job execution can run a Data Job one or more times. "
            "It can be passed externally (in case of external re-tries are considered part of 1 execution).",
        )
        config_builder.add(
            ATTEMPT_ID,
            "",
            True,
            "An identifier to be associated with the current VDK execution attempt."
            "If left empty it will be auto-generated. "
            "An instance of a running Data Job deployment is called an execution. "
            "Data Job execution can run a Data Job one or more times."
            "Each distinct run would a single attempt.",
        )


class EnvironmentVarsConfigPlugin:
    """
    Configuration loaded from environment variables.
    """

    def __normalize_key(self, key):
        return key.replace("-", "_").replace(".", "_").upper()

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
        upper_cased_env = {k.upper(): v for k, v in os.environ.items()}
        for key in config_keys:
            normalized_key_with_vdk_prefix = VDK_ + self.__normalize_key(key)
            normalized_key = self.__normalize_key(key)
            value = upper_cased_env.get(normalized_key)
            value_with_vdk_prefix = upper_cased_env.get(normalized_key_with_vdk_prefix)
            if value_with_vdk_prefix is not None:
                log.debug(
                    f"Found environment variable {normalized_key_with_vdk_prefix} for key {key}"
                )
                config_builder.set_value(key, value_with_vdk_prefix)
            elif value is not None:
                log.debug(f"Found environment variable {normalized_key} for key {key}")
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
        description = f"""Used only during vdk run  - load configuration specified in
config.ini file in the data job's root directory.
It can be overridden by environment variables configuration (set by operators in Cloud deployment or by users locally).
         """

        config_builder.add(
            key="__config_provider__job config ini",
            default_value="always_enabled",
            description=description,
        )
        if (
            self.__job_path
            and self.__job_path.exists()
            and self.__job_path.is_dir()
            and self.__job_path.joinpath("config.ini").exists()
        ):
            log.info("Detected config.ini. Will try to read config.ini.")

            job_config = JobConfig(self.__job_path)
            config_builder.set_value(JobConfigKeys.TEAM.value, job_config.get_team())
            config_builder.set_value(
                JobConfigKeys.TEAM, job_config.get_team()
            )  # kept for backward compatibility
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_USER_ERROR.value,
                job_config.get_contacts_notified_on_job_failure_user_error(),
            )
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_SUCCESS.value,
                job_config.get_contacts_notified_on_job_success(),
            )
            config_builder.set_value(
                JobConfigKeys.NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR.value,
                job_config.get_contacts_notified_on_job_failure_platform_error(),
            )
            config_builder.set_value(
                JobConfigKeys.ENABLE_ATTEMPT_NOTIFICATIONS.value,
                job_config.get_enable_attempt_notifications(),
            )

            for key, value in job_config.get_vdk_options().items():
                config_builder.set_value(key, value)
