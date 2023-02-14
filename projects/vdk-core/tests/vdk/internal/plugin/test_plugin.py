# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

import pytest
from pluggy import PluginManager
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.hook_markers import hookspec
from vdk.api.plugin.plugin_registry import PluginException
from vdk.internal.plugin.plugin import PluginRegistry


class JokesHookSpec:
    @hookspec
    def get_a_joke(self, number: int):
        pass

    @hookspec(firstresult=True)
    def get_first_joke(self):
        pass


@pytest.fixture
def plugin_registry():
    plugin_registry = PluginRegistry()
    plugin_registry.add_hook_specs(JokesHookSpec)
    return plugin_registry


def test_plugin_hook_add_and_load(plugin_registry):
    meal_joke = "Money can't buy you happiness? Well, check this out, I bought myself a Happy Meal."
    programmer_joke = (
        "A Programmer was walking out of door for work, "
        "his wife said `while you’re out, buy some milk` and he never came home."
    )

    class FooBarPlugin:
        @hookimpl
        def get_a_joke(self, number: int):
            return programmer_joke if number % 2 == 0 else meal_joke

    plugin_registry.load_plugin_with_hooks_impl(FooBarPlugin(), "foo-bar-joke-plugin")

    assert plugin_registry.hook().get_a_joke(number=1) == [meal_joke]
    assert plugin_registry.hook().get_a_joke(number=12) == [programmer_joke]

    assert plugin_registry.has_plugin("foo-bar-joke-plugin")


def test_no_plugins_hook(plugin_registry):
    assert plugin_registry.hook().get_a_joke(number=1) == []


def test_plugin_hook_add_and_load_failed(plugin_registry):
    class BadPlugin:
        @hookimpl
        def get_a_joke(self, wrong_param: int):
            return "Huh!"

    with pytest.raises(PluginException):
        plugin_registry.load_plugin_with_hooks_impl(BadPlugin(), "bad-plugin")


def test_cannot_load_entrypoints_plugins():
    with patch(
        "vdk.internal.plugin.plugin_manager.VdkPluginManager", spec=PluginManager
    ) as mock_plugin_manager:
        mock_plugin_manager.hook = None
        mock_plugin_manager.load_setuptools_entrypoints.side_effect = Exception("foo")
        with pytest.raises(PluginException):
            plugin_registry = PluginRegistry("vdk.group.foo", mock_plugin_manager)
            plugin_registry.load_plugins_from_setuptools_entrypoints()


def test_plugin_blocked_name(plugin_registry):
    class FooBarPlugin:
        @hookimpl
        def get_a_joke(self, number: int):
            return "No joke."

    plugin_registry.plugin_manager().set_blocked("blocked-name")
    plugin_registry.load_plugin_with_hooks_impl(FooBarPlugin(), "blocked-name")


def test_order_for_firstonly_plugin_hookwrapper_error(plugin_registry):
    class WrapperPlugin:
        @hookimpl(hookwrapper=True)
        def get_first_joke(self):
            yield
            raise IndexError("foo")

    class FirstPluginWithError:
        @hookimpl(tryfirst=True)
        def get_first_joke(self):
            return "first"

    plugin_registry.load_plugin_with_hooks_impl(FirstPluginWithError(), "first")
    plugin_registry.load_plugin_with_hooks_impl(WrapperPlugin(), "wrapper")

    with pytest.raises(IndexError):
        plugin_registry.hook().get_first_joke()


def test_order_for_firstonly_plugin_error(plugin_registry):
    class LastPlugin:
        @hookimpl(trylast=True)
        def get_first_joke(self):
            return "joke"

    class FirstPluginWithError:
        @hookimpl(tryfirst=True)
        def get_first_joke(self):
            raise Exception("foo")

    plugin_registry.load_plugin_with_hooks_impl(FirstPluginWithError(), "first")
    plugin_registry.load_plugin_with_hooks_impl(LastPlugin(), "last")

    with pytest.raises(Exception):
        plugin_registry.hook().get_first_joke()


def test_order_for_firstonly_plugin(plugin_registry):
    class LastPlugin:
        @hookimpl(trylast=True)
        def get_first_joke(self):
            return "last joke"

    class MiddlePlugin:
        @hookimpl
        def get_first_joke(self):
            return "middle joke"

    class FirstPlugin:
        @hookimpl(tryfirst=True)
        def get_first_joke(self):
            x = 1 + 1  # return nothing

    plugin_registry.load_plugin_with_hooks_impl(FirstPlugin(), "first")
    plugin_registry.load_plugin_with_hooks_impl(MiddlePlugin(), "middle")
    plugin_registry.load_plugin_with_hooks_impl(LastPlugin(), "last")

    assert plugin_registry.hook().get_first_joke() == "middle joke"


def test_order_for_normal_plugin(plugin_registry):
    class LastPlugin:
        @hookimpl(trylast=True)
        def get_a_joke(self, number: int):
            return "last joke"

    class MiddlePlugin:
        @hookimpl
        def get_a_joke(self, number: int):
            return "middle joke"

    class FirstPlugin:
        @hookimpl(tryfirst=True)
        def get_a_joke(self, number: int):
            x = 1 + 1  # return nothing

    plugin_registry.load_plugin_with_hooks_impl(FirstPlugin(), "first")
    plugin_registry.load_plugin_with_hooks_impl(MiddlePlugin(), "middle")
    plugin_registry.load_plugin_with_hooks_impl(LastPlugin(), "last")

    assert plugin_registry.hook().get_a_joke(number=1) == ["middle joke", "last joke"]


def test_order_for_plugin_error(plugin_registry):
    recorder = []

    class LastPlugin:
        @hookimpl(trylast=True)
        def get_a_joke(self, number: int):
            recorder.append("last")
            return "last joke"

    class MiddlePlugin:
        @hookimpl(hookwrapper=True)
        def get_a_joke(self, number: int):
            recorder.append("before")
            yield
            recorder.append("after")

    class FirstPlugin:
        @hookimpl(tryfirst=True)
        def get_a_joke(self, number: int):
            recorder.append("first")
            raise Exception("")

    plugin_registry.load_plugin_with_hooks_impl(FirstPlugin(), "first")
    plugin_registry.load_plugin_with_hooks_impl(MiddlePlugin(), "middle")
    plugin_registry.load_plugin_with_hooks_impl(LastPlugin(), "last")

    with pytest.raises(Exception):
        plugin_registry.hook().get_a_joke(number=1)

    assert recorder == ["before", "first", "after"]


def test_hookwrapper_for_plugin_error(plugin_registry):
    """
    Here we test how we can handle error and re-throw new one to end user.
    In the example we take that if functions threw IndexError then it must have been ArithmeticError really.
    """

    class MiddlePlugin:
        @hookimpl(hookwrapper=True)
        def get_a_joke(self, number: int):
            out = yield
            exc_type, exc_value, exc_traceback = out.excinfo
            if issubclass(exc_type, IndexError):
                raise ArithmeticError("change index to arithmetic error") from exc_value

    class FirstPlugin:
        @hookimpl(tryfirst=True)
        def get_a_joke(self, number: int):
            raise IndexError("")

    plugin_registry.load_plugin_with_hooks_impl(FirstPlugin(), "first")
    plugin_registry.load_plugin_with_hooks_impl(MiddlePlugin(), "middle")

    with pytest.raises(ArithmeticError):
        plugin_registry.hook().get_a_joke(number=1)
