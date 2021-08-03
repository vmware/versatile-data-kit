# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from taurus.api.plugin.hook_markers import hookimpl
from taurus.vdk.builtin_plugins.config.config_help import ConfigHelpPlugin
from taurus.vdk.core.config import ConfigurationBuilder
from taurus.vdk.test_utils.util_funcs import cli_assert_equal
from taurus.vdk.test_utils.util_funcs import CliEntryBasedTestRunner


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


def test_cli_config_help():
    runner = CliEntryBasedTestRunner(ConfigHelpPlugin(), TestConfigPlugin())
    result = runner.invoke(["config-help"])

    cli_assert_equal(0, result)

    # print(result.output)
    assert "test provider" in result.output
    assert "test provider description" in result.output
    assert "TEST_VARIABLE_KEY" in result.output
    assert "var description" in result.output
    assert "to-be-shown-default-value" in result.output
