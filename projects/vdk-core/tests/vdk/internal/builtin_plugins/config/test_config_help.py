# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.config.config_help import ConfigHelpPlugin
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.test_utils.util_funcs import cli_assert_equal
from vdk.plugin.test_utils.util_funcs import CliEntryBasedTestRunner


class TestConfigPlugin:
    @hookimpl
    def vdk_configure(self, config_builder: ConfigurationBuilder) -> None:
        config_builder.add(
            "__config_provider__ test provider",
            None,
            False,
            "test provider description",
        )
        config_builder.add("TEST_VARIABLE_KEY", None, False, "var description")
        config_builder.add(
            "KEY_WITH_DEFAULT", "to-be-shown-default-value", True, "key with default"
        )
        config_builder.add("key_bool", False, True, "bool")
        config_builder.add("key_int", 1, False, "int")
        config_builder.add("key_no_description", 1)
        config_builder.add("key_misconfigured_description", None, True, 111)
        config_builder.add("key_sensitive", 'default-value', True, 'key-description', True)


def test_cli_config_help():
    runner = CliEntryBasedTestRunner(ConfigHelpPlugin(), TestConfigPlugin())
    result = runner.invoke(["config-help"])

    cli_assert_equal(0, result)

    # print(result.output)
    assert "test provider" in result.output
    assert "test provider description" in result.output
    assert "test_variable_key" in result.output
    assert "var description" in result.output
    assert "to-be-shown-default-value" in result.output
    assert "key_bool" in result.output
    assert "key_int" in result.output
    assert "key_misconfigured_description" in result.output
    assert "key_misconfigured_description" in result.output
    assert "key_sensitive" in result.output
    assert "SENSITIVE: " in result.output
