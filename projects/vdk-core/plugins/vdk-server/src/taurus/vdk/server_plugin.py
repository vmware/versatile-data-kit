# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
VDK Server plugin script.
"""
import logging

import click
from click import Context
from taurus.vdk.installer import Installer
from taurus.api.plugin.hook_markers import hookimpl

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
    help="Removes a previous Control Service installation",
)
def server(install, uninstall):

    if (not install and not uninstall) or (install and uninstall):
        click.echo("Exactly one of --install or --uninstall options should be specified")
    else:
        installer = Installer()
        if install:
            installer.install()
        else:
            installer.uninstall()


@hookimpl
def vdk_command_line(root_command: click.Group):
    root_command.add_command(server)
