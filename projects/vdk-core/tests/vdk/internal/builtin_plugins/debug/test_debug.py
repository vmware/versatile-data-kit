# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.hook_markers import hookspec
from vdk.internal.builtin_plugins.debug.debug import HookRecorder
from vdk.internal.builtin_plugins.debug.debug import ParsedCall
from vdk.internal.plugin.plugin import PluginRegistry


def test_hook_recorder():
    plugin_registry = PluginRegistry()
    hook_recorder = HookRecorder(plugin_registry)

    class MySpec:
        @hookspec
        def hook_one(self, number: int):
            pass

        @hookspec
        def hook_two(self):
            pass

    class MyPlugin:
        @hookimpl
        def hook_one(self, number: int):
            print(number)

        @hookimpl
        def hook_two(self):
            print(2)
            plugin_registry.hook().hook_one(number=2)

    plugin_registry.add_hook_specs(MySpec)
    plugin_registry.load_plugin_with_hooks_impl(MyPlugin(), name="my-plugin")

    plugin_registry.hook().hook_one(number=1)
    plugin_registry.hook().hook_two()

    hook_recorder.finish_recording()

    assert hook_recorder.get_calls() == [
        ParsedCall("hook_one", {"number": 1}),
        ParsedCall("hook_two", {}),
        ParsedCall("hook_one", {"number": 2}),
    ]
