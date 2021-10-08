# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.control.command_groups.common_group.default import (
    reset_default_command,
)
from vdk.internal.control.command_groups.common_group.default import set_default_command
from vdk.internal.control.command_groups.job.create import create
from vdk.internal.control.command_groups.job.delete import delete
from vdk.internal.control.command_groups.job.deploy_cli import deploy
from vdk.internal.control.command_groups.job.download_job import download_job
from vdk.internal.control.command_groups.job.download_key import download_key
from vdk.internal.control.command_groups.job.execute import execute
from vdk.internal.control.command_groups.job.list import list_command
from vdk.internal.control.command_groups.job.properties import properties_command
from vdk.internal.control.command_groups.job.show import show_command
from vdk.internal.control.command_groups.login_group.login import login
from vdk.internal.control.command_groups.logout_group.logout import logout
from vdk.internal.control.configuration.default_options import DefaultOptions
from vdk.internal.control.plugin import control_plugin_manager
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.control_cli_plugin import control_service_configuration


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(login)
    root_command.add_command(logout)
    root_command.add_command(delete)
    root_command.add_command(create)
    root_command.add_command(download_key)
    root_command.add_command(list_command)
    root_command.add_command(deploy)
    root_command.add_command(execute)
    root_command.add_command(download_job)
    root_command.add_command(set_default_command)
    root_command.add_command(reset_default_command)
    root_command.add_command(show_command)
    root_command.add_command(properties_command)

    plugins = control_plugin_manager.Plugins()
    default_options = DefaultOptions(plugins)
    if default_options.get_default_map():
        root_command.context_settings["default_map"] = default_options.get_default_map()


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    """ """
    control_service_configuration.add_definitions(config_builder)
