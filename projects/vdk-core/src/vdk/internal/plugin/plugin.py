# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
from typing import List
from typing import Tuple

from vdk.api.plugin import hook_markers
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.api.plugin.plugin_registry import PluginException
from vdk.api.plugin.plugin_registry import PluginHookRelay
from vdk.internal.core.errors import ErrorMessage
from vdk.internal.core.errors import ResolvableBy
from vdk.internal.plugin.plugin_manager import VdkPluginManager
from vdk.internal.util.utils import log_plugin_load_fail


log = logging.getLogger(__name__)


class PluginRegistry(IPluginRegistry):
    """
    Manage plugins.
    Plugin consist of two things
    * Specification (see hookspec decorator) which define method (name and arguments)
    * Implementation (see hookimpl decorator) which must matches method name and subset of the arguments

    Plugin Registry will automatically load all plugins registered through setup tools entry points for vdk.plugin.run
    And provide methods for adding new specs and implementations.

    see https://pluggy.readthedocs.io/en/latest/#how-does-it-work
    """

    def __init__(self, group_name=hook_markers.GROUP_NAME, plugin_manager=None):
        self.__plugin_manager = (
            VdkPluginManager(group_name) if plugin_manager is None else plugin_manager
        )
        self.__hook_relay = PluginHookRelay(self.__plugin_manager.hook)
        self.__group_name = group_name
        self.__plugin_load_success = False

    def __str__(self):
        s = (
            f"PluginRegistry(group_name={self.__group_name})"
            f"Plugins: " + f"{os.linesep}".join([str(v) for v in self.list_plugins()])
        )
        return s

    def plugin_manager(self):
        return self.__plugin_manager

    def load_plugins_from_setuptools_entrypoints(self) -> None:
        log.debug("Loading plugins")

        try:
            self.__plugin_manager.load_setuptools_entrypoints(self.__group_name)
        except ImportError as e:
            log_plugin_load_fail(ResolvableBy.USER_ERROR, log, e, self.__group_name)
            raise PluginException from e
        except Exception as e:
            log_plugin_load_fail(ResolvableBy.PLATFORM_ERROR, log, e, self.__group_name)
            raise PluginException from e

        plugins = self.__plugin_manager.list_name_plugin()
        log.info(
            f"Following plugins from setup entrypoints have been discovered and registered: {plugins}"
        )
        self.__plugin_load_success = True

    def is_plugin_load_success(self):
        return self.__plugin_load_success

    def list_plugins(self) -> List[Tuple[str, str]]:
        return self.__plugin_manager.list_name_plugin()

    def has_plugin(self, name: str) -> bool:
        return self.__plugin_manager.has_plugin(name)

    def load_plugin_with_hooks_impl(
        self, module_or_class_with_hook_impls: object, name: str = None
    ) -> None:
        """
        Load new plugin with hook implementations

        :param module_or_class_with_hook_impls: can be module (python package) or class or class instance
        :param name: the name of the plugin. If None it will be the cannonical name of the module/class passed.
        which contain the hook implementations
        """
        try:
            plugin_name = self.__plugin_manager.register(
                module_or_class_with_hook_impls, name=name
            )
            if plugin_name:
                log.debug(f"Registered new plugin: {plugin_name}")
            else:
                log.warning(
                    f"Failed to register plugin {name}. Most likely the plugin name has been forbidden"
                )
        except Exception as e:
            raise PluginException(
                f"""Failed to load plugin
                Failed to load plugin with name  '{name}' and module/class '{module_or_class_with_hook_impls}'
                Troubleshooting options:
                1. Check what plugins are installed (use `pip list` command) and see if there are any issues.
                2. Revert to previous stable version of the plugin or CLI plugin (pip install vdk-plugin-name==version)
                3. Reinstall the app in a new clean environment
                """
            ) from e

    def add_hook_specs(self, module_or_class_with_hookspecs: object):
        self.__plugin_manager.add_hookspecs(module_or_class_with_hookspecs)

    def hook(self) -> PluginHookRelay:
        """
        Hook relay which to use to execute the plugin hooks with.

        You can also cast it to the HookSpec class with the hook you want to invoke to get auto-completion and so on.
        results: List = cast(CoreHookSpecs, plugin_registry.hook()).some_hook()
        But NOTE that the return result is a list of the results of all hooks implementations
        (unless hook spec is firstresult=True)
        """
        return self.__hook_relay
