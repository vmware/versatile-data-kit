# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import Tuple

import pluggy


class PluginHookRelay:
    """
    Helper class to relay method execution of underlying hook.
    It's merely to enable autocomplete and reading documentation of hook spec when using it.
    For each declared function spec, add method with same name and implementation:
    `return self.pm.hook.method_name`

    When invoking the hook note that return of the hook result is an array of all results (for all plugins hooks)
    unless hook is marked with firstresult=True

    """

    def __init__(self, hook_relay):
        self.__hook_relay = hook_relay

    def __dir__(self):
        return dir(self.__hook_relay)

    def __getattr__(self, key):
        hook = getattr(self.__hook_relay, key)
        self.__dict__[key] = hook
        return hook


class PluginException(Exception):
    """
    Exception thrown if error happens when working with plugins.
    """

    pass


"""
Alias for the type of plugin hook call result returned in hookWrapper=True types of plugin hooks
"""
HookCallResult = pluggy.callers._Result


class IPluginRegistry(metaclass=ABCMeta):
    """
    Plugins are basically python modules that implement one or more plugin hooks with some kind of specification.
    Specification is a method name and signature that must be implemented and is decorated with hook_markers.hookspec

    For example we can have hookspec defined this way:

    .. highlight:: python
    .. code-block:: python
        class DataJobRunHookSpec
            @hookspec
            def configure_job(self, context: JobContext, configuration: Config):
                pass

    Create a new plugin hook is simply implementing a method with the same name and marked with hook_markers.hookimpl.

    .. highlight:: python
    .. code-block:: python
        @hookimpl()
        def configure_job(self, context: JobContext, configuration: Config):
            ...

    """

    @abstractmethod
    def list_plugins(self) -> List[Tuple[str, str]]:
        """
        :return: pairs of plugin name and plguin module/class which holds the plugin hook implementations
        """

    @abstractmethod
    def has_plugin(self, name: str) -> bool:
        """
        :param name: the name of the plugin
        :return: Returns true if a plugin has been loaded.
        """
        pass

    @abstractmethod
    def load_plugin_with_hooks_impl(
        self, module_or_class_with_hook_impls: object, name: str
    ) -> None:
        """
        Load new plugin with hook implementations

        :param module_or_class_with_hook_impls: can be module (python package) or class or class instance
        :param name: the name of the plugin. If None it will be the canonical name of the module/class passed.
        which contain the hook implementations
        """
        pass

    @abstractmethod
    def add_hook_specs(self, module_or_class_with_hookspecs: object) -> None:
        """
        Add hook specifications. They must be annotated with hook_markers.hookimpl.
        :param module_or_class_with_hookspecs:
        :return:
        """
        pass

    @abstractmethod
    def hook(self) -> PluginHookRelay:
        """
        Returns hook relay use to execute the plugin hooks.
        If there is plugin hook with spec: vdk_initialize(context: JobContext)
        Then all its implementations will be invoked with hook().vdk_initialize(context=job_context)

        Note that hook must be invoked using keyword arguments.

        :return: Hook relay which to use to execute the plugin hooks with
        """
        pass
