# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.control.plugin.control_plugin_manager import Plugins


def test_plugin_default_commands_options():
    default_options = {"login": {"oauth2_authorization_url": "http://foo"}}

    class FooBarPlugin:
        from vdk.api.control.plugin.markers import hookimpl

        @hookimpl
        def get_default_commands_options(self):
            return default_options

    plugins = Plugins(load_registered=False)
    plugins.load_builtin_plugin(FooBarPlugin())
    assert plugins.hook().get_default_commands_options() == default_options


def test_no_plugins_default_commands_options():
    plugins = Plugins(load_registered=False)
    assert plugins.hook().get_default_commands_options() is None
