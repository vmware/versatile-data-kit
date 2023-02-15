# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.control_cli_plugin import vdk_plugin_control_cli
from vdk.plugin.control_cli_plugin.control_service_configuration import (
    CONTROL_SAMPLE_JOB_DIRECTORY,
)
from vdk.plugin.control_cli_plugin.control_service_configuration import (
    CONTROL_SERVICE_REST_API_URL,
)
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


def test_vdk_plugin_control_cli():
    vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli)
    result = vdk_runner.invoke(["deploy", "--help"])

    cli_assert_equal(0, result)


def test_vdk_plugin_control_cli_configuration_defined():
    vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli)
    result = vdk_runner.invoke(["config-help"])

    cli_assert_equal(0, result)
    assert (
        CONTROL_SAMPLE_JOB_DIRECTORY.lower() in str(result.output).lower()
        and CONTROL_SERVICE_REST_API_URL.lower() in str(result.output).lower()
    ), (
        "Expected to find definitions of CONTROL_SERVICE_REST_API_URL & CONTROL_SAMPLE_JOB_DIRECTORY in result output "
        f"but did not. result output is: {result.output}"
    )


def test_vdk_plugin_control_cli_configuration_applied_to_vdk_control_cli():
    class MyConfig:
        @staticmethod
        @hookimpl
        def vdk_configure(config_builder: ConfigurationBuilder) -> None:
            config_builder.set_value("API_TOKEN", "api-token")
            config_builder.set_value("CONTROL_HTTP_VERIFY_SSL", True)
            config_builder.set_value("CONTROL_HTTP_CONNECT_RETRIES", 12)
            config_builder.set_value("API_TOKEN_AUTHORIZATION_URL", "new_value")

    # patch.dict would reset all changed env during the test after.
    with mock.patch.dict(os.environ, {"VDK_API_TOKEN_AUTHORIZATION_URL": "original"}):
        os.environ.pop("VDK_API_TOKEN", None)
        os.environ.pop("VDK_CONTROL_HTTP_VERIFY_SSL", None)
        os.environ.pop("CONTROL_HTTP_CONNECT_RETRIES", None)

        vdk_runner = CliEntryBasedTestRunner(vdk_plugin_control_cli, MyConfig())
        result = vdk_runner.invoke(["deploy", "--help"])

        cli_assert_equal(0, result)
        assert VDKConfig().api_token == "api-token"
        assert VDKConfig().http_verify_ssl
        assert VDKConfig().http_connect_retries == 12
        assert VDKConfig().api_token_authorization_url == "original"
