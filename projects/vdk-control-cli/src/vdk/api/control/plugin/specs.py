# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Hook Specs can be declared here.
Hooks specs need to be marked with @hookspec decorator annotation.

Hook Implementation need to be marked with @hookimpl decorator and have the same name.
"""
from vdk.api.control.plugin.markers import hookspec


class CliHookSpecs:
    """
    Aggregation of different VDK CLI hooks that can be implemented.

    To implement a hook you only need to create function with same name and specify @hookimpl decorator on it.
    The only other thing is to register it so it can be discovered and you can see README.md for how to do this.
    """

    @hookspec(firstresult=True)
    def get_default_commands_options(self):
        """
        Hook to be invoked when initializing default options of the CLI.
        Specify what default options for command line arguments the tool should use.
        User can still override them with command line arguments.
        Only the first discovered hook function is executed.

        :return: new default options to use.
            It matches default_map in https://click.palletsprojects.com/en/7.x/commands/#overriding-

        For example for command cli login --oauth2-authorize-uri
        the following should be returned (note that dashes are replaced with underscore)
        { "login" : { "oauth2_authorize_uri": "new_default_value" } }
        """
        pass
