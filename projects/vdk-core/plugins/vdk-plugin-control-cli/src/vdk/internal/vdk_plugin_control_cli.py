# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from taurus.vdk.control.command_groups.common_group.default import (
    reset_default_command,
)
from taurus.vdk.control.command_groups.common_group.default import set_default_command
from taurus.vdk.control.command_groups.job.create import create
from taurus.vdk.control.command_groups.job.delete import delete
from taurus.vdk.control.command_groups.job.deploy_cli import deploy
from taurus.vdk.control.command_groups.job.download_job import download_job
from taurus.vdk.control.command_groups.job.download_key import download_key
from taurus.vdk.control.command_groups.job.execute import execute
from taurus.vdk.control.command_groups.job.list import list_command
from taurus.vdk.control.command_groups.job.properties import properties_command
from taurus.vdk.control.command_groups.job.show import show_command
from taurus.vdk.control.command_groups.login_group.login import login
from taurus.vdk.control.command_groups.logout_group.logout import logout
from taurus.vdk.control.configuration.default_options import DefaultOptions
from taurus.vdk.plugin import control_plugin_manager
from vdk.api.plugin.hook_markers import hookimpl


def __replace_vdkcli_with_vdk(command):
    command.help = str.replace(command.help, "vdkcli", "vdk")
    return command


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(__replace_vdkcli_with_vdk(login))
    root_command.add_command(__replace_vdkcli_with_vdk(logout))
    root_command.add_command(__replace_vdkcli_with_vdk(delete))
    root_command.add_command(__replace_vdkcli_with_vdk(create))
    root_command.add_command(__replace_vdkcli_with_vdk(download_key))
    root_command.add_command(__replace_vdkcli_with_vdk(list_command))
    root_command.add_command(__replace_vdkcli_with_vdk(deploy))
    root_command.add_command(__replace_vdkcli_with_vdk(execute))
    root_command.add_command(__replace_vdkcli_with_vdk(download_job))
    root_command.add_command(__replace_vdkcli_with_vdk(set_default_command))
    root_command.add_command(__replace_vdkcli_with_vdk(reset_default_command))
    root_command.add_command(__replace_vdkcli_with_vdk(show_command))
    root_command.add_command(__replace_vdkcli_with_vdk(properties_command))

    plugins = control_plugin_manager.Plugins()
    default_options = DefaultOptions(plugins)
    if default_options.get_default_map():
        root_command.context_settings["default_map"] = default_options.get_default_map()
