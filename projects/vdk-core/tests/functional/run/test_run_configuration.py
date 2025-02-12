# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import Optional
from unittest import mock

from click.testing import Result
from functional.run import util
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.run.execution_results import ExecutionResult
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.statestore import CommonStoreKeys
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner
from vdk.plugin.test_utils.util_plugins import TestSecretsServiceClient


@mock.patch.dict(
    os.environ,
    {
        "VDK_OP_ID": "my-op-id",
        "VDK_EXECUTION_ID": "my-execution-id",
        "VDK_ATTEMPT_ID": "my-attempt-id",
    },
)
def test_run_check_attempt_execution_op_id_are_set_correctly():
    actual_ids = []

    class PrintIdPlugin:
        @hookimpl(tryfirst=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            actual_ids.append(
                context.core_context.state.get(CommonStoreKeys.ATTEMPT_ID)
            )
            actual_ids.append(
                context.core_context.state.get(CommonStoreKeys.EXECUTION_ID)
            )
            actual_ids.append(context.core_context.state.get(CommonStoreKeys.OP_ID))
            return None  # continue with next hook impl.

    runner = CliEntryBasedTestRunner(PrintIdPlugin())

    result: Result = runner.invoke(["run", util.job_path("simple-job")])

    cli_assert_equal(0, result)
    assert actual_ids == ["my-attempt-id", "my-execution-id", "my-op-id"]


def test_run_check_log_level_configured_correctly():
    debug_log_message = "DEBUG LOG 1123581321"

    class DummyDebugLog:
        @hookimpl(tryfirst=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            # -v may not apply to vdk packages which are controlled separately
            logging.getLogger("other").debug(debug_log_message)
            return None  # continue with next hook impl.

    runner = CliEntryBasedTestRunner(DummyDebugLog())

    # -v DEBUG means we print debug logs
    result: Result = runner.invoke(["-v", "DEBUG", "run", util.job_path("simple-job")])
    cli_assert_equal(0, result)
    assert debug_log_message in result.output

    # -v INFO - debug logs should not be printed.
    result: Result = runner.invoke(["-v", "INFO", "run", util.job_path("simple-job")])
    cli_assert_equal(0, result)
    assert debug_log_message not in result.output


def test_run_config_variables_are_set():
    class DebugConfigLog:
        def __init__(self):
            self.config = None

        @hookimpl(tryfirst=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            self.config = context.core_context.configuration
            return None  # continue with next hook impl.

    with mock.patch.dict(
        os.environ,
        {
            "VDK_ATTEMPT_ID": "env-attempt-id-overrides-config-ini",
            "vdk_execution_id": "lower-case-env-exec-id",
        },
    ):
        config_log = DebugConfigLog()
        runner = CliEntryBasedTestRunner(config_log)
        result: Result = runner.invoke(["run", util.job_path("job-with-config-ini")])
        cli_assert_equal(0, result)

        assert (
            config_log.config.get_value("attempt_id")
            == "env-attempt-id-overrides-config-ini"
        )
        assert config_log.config.get_value("execution_id") == "lower-case-env-exec-id"
        assert (
            config_log.config.get_value("other_config")
            == "other-config-from-config-ini"
        )


def test_run_secrets_override_config_vars():
    class DebugConfigLog:
        def __init__(self):
            self.config = None
            self.secrets_client = TestSecretsServiceClient()

        @hookimpl(tryfirst=True)
        def initialize_job(self, context: JobContext):
            context.secrets.set_secrets_factory_method(
                "default", lambda: self.secrets_client
            )
            secrets = context.job_input.get_all_secrets()
            secrets["LOG_EXCEPTION_FORMATTER"] = "plain"
            secrets["IRRELEVANT_SECRET"] = "not relevant at all"
            context.job_input.set_all_secrets(secrets)

        @hookimpl(trylast=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            self.config = context.core_context.configuration
            return None  # continue with next hook impl.

    config_log = DebugConfigLog()
    runner = CliEntryBasedTestRunner(config_log)
    result: Result = runner.invoke(["run", util.job_path("simple-job-config-ini")])
    cli_assert_equal(0, result)
    # secrets that match config keys are overridden, even if config.ini sets them explicitly
    assert config_log.config.get_value("log_exception_formatter") == "plain"
    # secrets that do not match any config key do not leak in the config object
    assert config_log.config.get_value("irrelevant_secret") is None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_LOG_EXCEPTION_FORMATTER": "pretty",
        },
    ):
        config_log = DebugConfigLog()
        runner = CliEntryBasedTestRunner(config_log)
        result: Result = runner.invoke(["run", util.job_path("simple-job")])
        cli_assert_equal(0, result)
        # secrets that match config keys but are configured using env variables are NOT overridden
        assert config_log.config.get_value("log_exception_formatter") == "pretty"
        # secrets that do not match any config key do not leak in the config object
        assert config_log.config.get_value("irrelevant_secret") is None


def test_run_secrets_override_config_vars_section():
    class DebugConfigLog:
        def __init__(self):
            self.config = None
            self.secrets_client = TestSecretsServiceClient()

        @hookimpl
        def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
            config_builder.add(key="config_option", default_value="")
            config_builder.add(key="config_option", default_value="", section="first")

        @hookimpl(tryfirst=True)
        def initialize_job(self, context: JobContext):
            context.secrets.set_secrets_factory_method(
                "default", lambda: self.secrets_client
            )
            secrets = context.job_input.get_all_secrets()
            secrets["FIRST_CONFIG_OPTION"] = "from_section"
            secrets["CONFIG_OPTION"] = "from_default"
            secrets["IRRELEVANT_SECRET"] = "not relevant at all"
            context.job_input.set_all_secrets(secrets)

        @hookimpl(trylast=True)
        def run_job(self, context: JobContext) -> Optional[ExecutionResult]:
            self.config = context.core_context.configuration
            return None  # continue with next hook impl.

    config_log = DebugConfigLog()
    runner = CliEntryBasedTestRunner(config_log)
    result: Result = runner.invoke(
        ["run", util.job_path("simple-job-config-ini-sections")]
    )
    cli_assert_equal(0, result)

    # secrets that match config keys in the default section are overridden, even if config.ini sets them explicitly
    assert config_log.config.get_value("config_option") == "from_default"
    # secrets that match config keys in a section are overridden, even if config.ini sets them explicitly
    assert (
        config_log.config.get_value("config_option", section="first") == "from_section"
    )
    # secrets that do not match any config key do not leak in the config object
    assert config_log.config.get_value("irrelevant_secret") is None

    with mock.patch.dict(
        os.environ,
        {
            "VDK_CONFIG_OPTION": "from_default_env_var",
            "VDK_FIRST_CONFIG_OPTION": "from_first_env_var",
        },
    ):
        config_log = DebugConfigLog()
        runner = CliEntryBasedTestRunner(config_log)
        result: Result = runner.invoke(["run", util.job_path("simple-job")])
        cli_assert_equal(0, result)

        # secrets that match config keys in the default section are overridden, even if config.ini sets them explicitly
        assert config_log.config.get_value("config_option") == "from_default_env_var"
        # secrets that match config keys in a section are overridden, even if config.ini sets them explicitly
        assert (
            config_log.config.get_value("config_option", section="first")
            == "from_first_env_var"
        )
        # secrets that do not match any config key do not leak in the config object
        assert config_log.config.get_value("irrelevant_secret") is None
        # secrets that match config keys but are configured using env variables are NOT overridden
