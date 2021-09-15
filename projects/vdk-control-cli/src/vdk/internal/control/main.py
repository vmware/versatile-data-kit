# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click_log
from vdk.internal.control.command_groups.job.download_job import download_job
from vdk.internal.control.command_groups.job.properties import properties_command
from vdk.internal.control.command_groups.job.show import show_command
from vdk.internal.control.configuration.vdk_config import VDKConfig

"""
This the starting point for the Python vdk console script.
"""

import logging

import click

from vdk.internal.control.command_groups.login_group.login import login
from vdk.internal.control.command_groups.logout_group.logout import logout
from vdk.internal.control.command_groups.version_group.version import version
from vdk.internal.control.command_groups.job.create import create
from vdk.internal.control.command_groups.job.delete import delete
from vdk.internal.control.command_groups.job.deploy_cli import deploy
from vdk.internal.control.command_groups.job.download_key import download_key
from vdk.internal.control.command_groups.job.list import list_command
from vdk.internal.control.command_groups.job.execute import execute
from vdk.internal.control.command_groups.common_group.default import set_default_command
from vdk.internal.control.command_groups.common_group.default import (
    reset_default_command,
)
from vdk.internal.control.configuration.default_options import DefaultOptions
from vdk.internal.control.configuration.log_config import configure_loggers
from vdk.internal.control.plugin import control_plugin_manager

log = logging.getLogger(__name__)


@click.group(
    help="""Command line tool for Data Jobs lifecycle management.

The cli enables you to conveniently create by template, deploy, list and manage Data Jobs in the Cloud.

See commands below. For each command you can see its help for more details. For example: vdk create --help

\b
Following environment variables can be used to customize the CLI (usually you want to leave them by default):
    - VDK_BASE_CONFIG_FOLDER - Override local base configuration folder (by default $HOME folder) .
                               Use in case multiple users need to login (e.g in case of automation) on same machine.

Examples:

\b
# Show help of deploy command (can be done for each command)
vdk deploy --help

\b
# Set default team for all commands
vdk set-default --team taurus
"""
)
@click.option(
    "-d",
    "--dev",
    is_flag=True,
    default=False,
    help="Run in a developer mode - will print extra context on each log line.",
)
@click_log.simple_verbosity_option(logging.getLogger())
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, dev: bool):

    if dev:
        configure_loggers(op_id=VDKConfig().op_id)
    else:
        click_log.basic_config(logging.getLogger())

    plugins = control_plugin_manager.Plugins()
    default_options = DefaultOptions(plugins)
    ctx.default_map = default_options.get_default_map()


def run():
    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(delete)
    cli.add_command(create)
    cli.add_command(download_key)
    cli.add_command(list_command)
    cli.add_command(deploy)
    cli.add_command(version)
    cli.add_command(execute)
    cli.add_command(set_default_command)
    cli.add_command(reset_default_command)
    cli.add_command(download_job)
    cli.add_command(show_command)
    cli.add_command(properties_command)

    cli()


if __name__ == "__main__":
    run()
