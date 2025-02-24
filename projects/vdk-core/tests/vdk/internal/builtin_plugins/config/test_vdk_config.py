# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

from vdk.internal.builtin_plugins.config.vdk_config import EnvironmentVarsConfigPlugin
from vdk.internal.core.config import ConfigurationBuilder


@mock.patch.dict(
    os.environ,
    {"VDK_OPTION": "high", "OPTION": "low", "no_prefixed_option": "value"},
)
def test_vdk_config_env_variable_vdk_prefix_prio():
    envVarsConfig = EnvironmentVarsConfigPlugin()
    configuration_builder = ConfigurationBuilder()
    configuration_builder.add("option", "")
    configuration_builder.add("no_prefixed_option", "")

    envVarsConfig.vdk_configure(configuration_builder)

    assert configuration_builder.build().get_value("option") == "high"
    assert configuration_builder.build().get_value("no_prefixed_option") == "value"


@mock.patch.dict(
    os.environ,
    {
        "VDK_FIRST_OPTION": "high",
        "FIRST_OPTION": "low",
        "first_no_prefixed_option": "value",
    },
)
def test_vdk_config_env_variable_vdk_prefix_prio_section():
    envVarsConfig = EnvironmentVarsConfigPlugin()
    configuration_builder = ConfigurationBuilder()
    configuration_builder.add("option", "", section="first")
    configuration_builder.add("no_prefixed_option", "", section="first")

    envVarsConfig.vdk_configure(configuration_builder)

    assert configuration_builder.build().get_value("option", "first") == "high"
    assert (
        configuration_builder.build().get_value("no_prefixed_option", "first")
        == "value"
    )


@mock.patch.dict(
    os.environ,
    {"VDK_SOMETHING": "default_section", "VDK_FIRST_SOMETHING": "first_section"},
)
def test_vdk_config_env_variable_overrides_per_section():
    envVarsConfig = EnvironmentVarsConfigPlugin()
    configuration_builder = ConfigurationBuilder()
    configuration_builder.add("something", "")
    configuration_builder.add("something", "", section="first")
    configuration_builder.add("something", "second_section", section="second")

    envVarsConfig.vdk_configure(configuration_builder)

    assert configuration_builder.build().get_value("something") == "default_section"
    assert (
        configuration_builder.build().get_value("something", section="first")
        == "first_section"
    )
    assert (
        configuration_builder.build().get_value("something", section="second")
        == "second_section"
    )


@mock.patch.dict(
    os.environ,
    {"VDK_OPTION_WITH_DOTS": "value1", "no_prefix_option_dots": "value2"},
)
def test_vdk_config_env_variable_dots_replaced():
    envVarsConfig = EnvironmentVarsConfigPlugin()
    configuration_builder = ConfigurationBuilder()
    configuration_builder.add("option.with.dots", "")
    configuration_builder.add("no.prefix.option.dots", "")

    envVarsConfig.vdk_configure(configuration_builder)
    assert configuration_builder.build().get_value("option.with.dots") == "value1"
    assert configuration_builder.build().get_value("no.prefix.option.dots") == "value2"


@mock.patch.dict(
    os.environ,
    {"VDK_OPTION_WITH_DASH": "value1", "no_prefix_option_dash": "value2"},
)
def test_vdk_config_env_variable_dash_replaced():
    envVarsConfig = EnvironmentVarsConfigPlugin()
    configuration_builder = ConfigurationBuilder()
    configuration_builder.add("option-with-dash", "")
    configuration_builder.add("no-prefix-option-dash", "")

    envVarsConfig.vdk_configure(configuration_builder)

    assert configuration_builder.build().get_value("option-with-dash") == "value1"
    assert configuration_builder.build().get_value("no-prefix-option-dash") == "value2"
