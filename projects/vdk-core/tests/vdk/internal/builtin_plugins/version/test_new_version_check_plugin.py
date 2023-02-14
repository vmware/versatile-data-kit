# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Dict
from unittest.mock import MagicMock
from unittest.mock import patch

from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.version import new_version_check_plugin
from vdk.internal.builtin_plugins.version import version
from vdk.internal.builtin_plugins.version.new_version_check_plugin import new_package
from vdk.internal.builtin_plugins.version.new_version_check_plugin import (
    NewVersionCheckPlugin,
)
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext
from vdk.internal.core.statestore import StateStore


def build_configuration(plugin, config: Dict):
    conf_builder = ConfigurationBuilder()
    plugin.vdk_configure(config_builder=conf_builder)
    for k, v in config.items():
        conf_builder.set_value(k, v)
    configuration = conf_builder.build()
    return configuration


def build_core_context(plugin, config: Dict):
    conf = build_configuration(plugin, config)
    context = CoreContext(MagicMock(spec=IPluginRegistry), conf, StateStore())
    return context


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
@patch(f"click.echo", autospec=True)
def test_no_new_version_check(mock_click_echo, mock_list, mock_package):
    mock_package.return_value.check.return_value = False
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = build_core_context(
        check_plugin,
        {
            new_version_check_plugin.ConfigKey.PACKAGE_INDEX.value: "https://testing.package.index"
        },
    )
    check_plugin.vdk_exit(context)

    mock_package.assert_any_call(
        package_index="https://testing.package.index", package_name="vdk-core"
    )
    mock_package.assert_any_call(
        package_index="https://testing.package.index", package_name="dist"
    )

    # we verify no command is suggested to the user
    assert not mock_click_echo.mock_calls


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
@patch(f"click.echo", autospec=True)
def test_new_version_check(mock_click_echo, mock_list, mock_package):
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = build_core_context(
        check_plugin,
        {
            new_version_check_plugin.ConfigKey.PACKAGE_INDEX.value: "https://testing.package.index"
        },
    )
    check_plugin.vdk_exit(context)

    mock_package.assert_any_call(
        package_index="https://testing.package.index", package_name="vdk-core"
    )
    mock_package.assert_any_call(
        package_index="https://testing.package.index", package_name="dist"
    )

    # we verify the correctness of the command that is suggested to the user
    expected_command = "pip install --upgrade-strategy eager -U vdk-core dist --extra-index-url https://testing.package.index"
    assert any(
        filter(lambda c: expected_command in str(c), mock_click_echo.mock_calls)
    ), f"did not get expected substring inside message: {mock_click_echo.mock_calls}"


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
def test_new_version_check_skip_plugins(mock_list, mock_package):
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = build_core_context(
        check_plugin,
        {new_version_check_plugin.ConfigKey.VERSION_CHECK_PLUGINS.value: False},
    )
    check_plugin.vdk_exit(context)

    mock_package.assert_called_with(
        package_index="https://pypi.org", package_name="vdk-core"
    )


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
@patch(f"click.echo", autospec=True)
def test_new_version_check_empty_package_index(
    mock_click_echo, mock_list, mock_package
):
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = build_core_context(
        check_plugin, {new_version_check_plugin.ConfigKey.PACKAGE_INDEX.value: ""}
    )
    check_plugin.vdk_exit(context)

    # new line at the end verified this is the full command.
    expected_command = "pip install --upgrade-strategy eager -U vdk-core dist \\n"
    assert any(
        filter(lambda c: expected_command in str(c), mock_click_echo.mock_calls)
    ), f"did not get expected substring inside message: {mock_click_echo.mock_calls}"


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
def test_new_version_check_error(mock_list, mock_package):
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = MagicMock(spec=CoreContext)
    context.return_value.configuration.side_effect = Exception("foo")

    # must not fail, error is ignored.
    check_plugin.vdk_exit(context)

    mock_package.assert_not_called()


@patch(f"{new_package.__module__}.{new_package.__name__}", autospec=True)
@patch(
    f"{version.list_installed_plugins.__module__}.{version.list_installed_plugins.__name__}",
    autospec=True,
)
def test_new_version_check_disabled(mock_list, mock_package):
    mock_list.return_value = [("dist", "plugin")]

    check_plugin = NewVersionCheckPlugin()
    context = build_core_context(
        check_plugin,
        {new_version_check_plugin.ConfigKey.VERSION_CHECK_DISABLED.value: True},
    )
    check_plugin.vdk_exit(context)

    mock_package.assert_not_called()
