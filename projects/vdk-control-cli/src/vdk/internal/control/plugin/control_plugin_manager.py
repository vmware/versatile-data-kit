# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import pluggy as pluggy
from vdk.api.control.plugin.markers import PROJECT_NAME
from vdk.api.control.plugin.specs import CliHookSpecs

log = logging.getLogger(__name__)


class PluginHookRelay:
    """
    Helper class to relay method execution of underlying hook.
    It's merely to enable autocomplete and reading documentation of hook spec when using it.
    For each declared function spec, add method with same name and implementation:
    `return self.pm.hook.method_name`

    When invoking the hook note that return of the hook result is an array of all results (for all plugins hooks)
    unless hook is marked with firstresult=True

    """

    def __init__(self, pm: pluggy.PluginManager):
        self.pm = pm

    # TODO: in the future we should provide perhaps concrete object/class so it's more type safe and less error prone.
    # Currently it's possible to break the CLI if you specify incorrect value (e.g string where int is expected)
    def get_default_commands_options(self):
        return self.pm.hook.get_default_commands_options()  # pylint: disable=no-member


class Plugins:
    """
    Manage plugins.
    Plugin consist of two things
    * Specification (see hookspec decorator) which define method (name and arguments)
    * Implementation (see hookimpl decorator) which must matches method name and subset of the arguments

    see https://pluggy.readthedocs.io/en/latest/#how-does-it-work
    """

    def __init__(self, project_name=PROJECT_NAME, load_registered=True):
        """
        :param project_name: The project name under which the plugins are looked up
        :param load_registered: used in tests to disabled loading external plugins. True by default.
        """
        self.pm = pluggy.PluginManager(project_name)
        self.hook_relay = PluginHookRelay(self.pm)
        self.__add_hook_specs()
        if load_registered:
            self.__load_registered_plugins(project_name)

    def __load_registered_plugins(self, project_name: str) -> None:
        log.debug("Loading plugins")

        try:
            self.pm.load_setuptools_entrypoints(project_name)
        except Exception as e:
            # TODO: incorporate standard error handling
            log.exception(
                "what: "
                + "Detected plugins but failed to load them"
                + "why: "
                + "See exception for details"
                + "consequences: "
                + "The CLI tool will abort "
                + "countermeasures: "
                + "uninstall the plugin (pip uninstall) or see exception and fix the error"
            )
            raise e

        plugins = self.pm.list_name_plugin()
        log.debug(f"Following plugins have been discovered: {plugins}")

    def load_builtin_plugin(self, builtin_plugin_module):
        try:
            self.pm.register(builtin_plugin_module)
        except Exception as e:
            # TODO: incorporate standard error handling
            log.exception(
                "what: "
                + "Failed to load builtin plugins."
                + "why: "
                + "Most likely a bug. See exception for details"
                + "consequences: "
                + "The CLI tool will abort "
                + "countermeasures: "
                + "Revert to previous stable version, open ticket to SRE or fix the bug"
            )
            raise e

    def __add_hook_specs(self):
        self.pm.add_hookspecs(CliHookSpecs)

    def hook(self):
        """
        :return: Hook relay which to use to execute the plugin hooks with
        """
        return self.hook_relay
