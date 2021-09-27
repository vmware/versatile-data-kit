# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK Server plugin script.
"""
import logging

import click
from vdk.api.plugin.hook_markers import hookimpl
from vdk.plugin.server.installer import Installer

log = logging.getLogger(__name__)


@click.command(
    name="server",
    help="Installs (and runs) or uninstalls a local Control Service."
    """
         TODO: Add description
         """,
)
@click.option(
    "-i",
    "--install",
    is_flag=True,
    help="Installs a local Control Service.",
)
@click.option(
    "-u",
    "--uninstall",
    is_flag=True,
    help="Removes a previous Control Service installation.",
)
@click.option(
    "-s",
    "--status",
    is_flag=True,
    help="Returns whether a local Control Service is currently installed.",
)
def server(install, uninstall, status):
    flags = 0
    if install:
        flags += 1
    if uninstall:
        flags += 1
    if status:
        flags += 1

    if flags != 1:
        click.echo(
            "Exactly one of --install, --uninstall, or --status options should be specified"
        )
    else:
        installer = Installer()
        if install:
            installer.install()
        elif uninstall:
            installer.uninstall()
        else:
            installer.check_status()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(server)
